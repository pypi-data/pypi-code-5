"""Bayesian variant calling with FreeBayes.

http://bioinformatics.bc.edu/marthlab/FreeBayes
"""
import os
import shutil

from bcbio import bam
from bcbio.utils import file_exists
from bcbio.distributed.transaction import file_transaction
from bcbio.pipeline import config_utils
from bcbio.pipeline.shared import subset_variant_regions
from bcbio.provenance import do
from bcbio.variation import annotation, ploidy

def region_to_freebayes(region):
    if isinstance(region, (list, tuple)):
        chrom, start, end = region
        return "%s:%s..%s" % (chrom, start, end)
    else:
        return region

def _freebayes_options_from_config(items, aconfig, out_file, region=None):
    opts = []
    opts += ["--ploidy", str(ploidy.get_ploidy(items, region))]

    variant_regions = aconfig.get("variant_regions", None)
    target = subset_variant_regions(variant_regions, region, out_file)
    if target:
        if isinstance(target, basestring) and os.path.isfile(target):
            opts += ["--targets", target]
        else:
            opts += ["--region", region_to_freebayes(target)]
    #background = aconfig.get("call_background", None)
    #if background and os.path.exists(background):
    #    opts += ["--variant-input", background]
    return opts

def run_freebayes(align_bams, items, ref_file, assoc_files, region=None,
                  out_file=None):
    """Detect SNPs and indels with FreeBayes.
    """
    config = items[0]["config"]
    if out_file is None:
        out_file = "%s-variants.vcf" % os.path.splitext(align_bams[0])[0]
    if not file_exists(out_file):
        with file_transaction(out_file) as tx_out_file:
            cl = [config_utils.get_program("freebayes", config),
                  "-v", tx_out_file, "-f", ref_file, "--pvar", "0.7"]
            for align_bam in align_bams:
                bam.index(align_bam, config)
                cl += ["-b", align_bam]
            cl += _freebayes_options_from_config(items, config["algorithm"], out_file, region)
            do.run(cl, "Genotyping with FreeBayes", {})
        clean_vcf_output(out_file, _clean_freebayes_output, "nodups")
    ann_file = annotation.annotate_nongatk_vcf(out_file, align_bams, assoc_files["dbsnp"],
                                               ref_file, config)
    return ann_file

def _move_vcf(orig_file, new_file):
    """Move a VCF file with associated index.
    """
    for ext in ["", ".idx"]:
        to_move = orig_file + ext
        if os.path.exists(to_move):
            shutil.move(to_move, new_file + ext)

def _clean_freebayes_output(line):
    """Clean FreeBayes output to make post-processing with GATK happy.
    - Remove lines from FreeBayes outputs where REF/ALT are identical:
      2       22816178        .       G       G       0.0339196
      or there are multiple duplicate alleles:
      4       60594753        .       TGAAA   T,T
    - Remove Type=Int specifications which are not valid VCF and GATK chokes on.
    """
    if line.startswith("#"):
        line = line.replace("Type=Int,D", "Type=Integer,D")
        return line
    else:
        parts = line.split("\t")
        alleles = [x.strip() for x in parts[4].split(",")] + [parts[3].strip()]
        if len(alleles) == len(set(alleles)):
            return line
    return None

def clean_vcf_output(orig_file, clean_fn, name="clean"):
    """Provide framework to clean a file in-place, with the specified clean function.
    """
    base, ext = os.path.splitext(orig_file)
    out_file = "{0}-{1}{2}".format(base, name, ext)
    if not file_exists(out_file):
        with open(orig_file) as in_handle:
            with file_transaction(out_file) as tx_out_file:
                with open(out_file, "w") as out_handle:
                    for line in in_handle:
                        update_line = clean_fn(line)
                        if update_line:
                            out_handle.write(update_line)
        _move_vcf(orig_file, "{0}.orig".format(orig_file))
        _move_vcf(out_file, orig_file)
        with open(out_file, "w") as out_handle:
            out_handle.write("Moved to {0}".format(orig_file))
