import unittest, sys
import pyDNase
from pyDNase.footprinting import wellington
import numpy
class Test(unittest.TestCase):
    """Unit tests for pyDNase."""
        
    def test_BAM_reading(self):
        """Test BAM access"""
        reads = pyDNase.BAMHandler(pyDNase.example_reads())
        numpy.testing.assert_array_equal(reads["chr6,170863142,170863150,+"]["+"], numpy.array([1, 0, 0, 0, 1, 11, 1, 0]))
        numpy.testing.assert_array_equal(reads["chr6,170863142,170863150,+"]["-"], numpy.array([0, 1, 0, 0, 1, 0, 0, 1]))

    
    def test_BED_reading(self):
        """Testing BED files"""
        regions = pyDNase.GenomicIntervalSet(pyDNase.example_regions())
        self.assertEqual(str(regions), 'chr6\t170863142\t170863532\t0\t0.0\t+\n')
        
    def test_footprinting(self):
        """Test footprinting"""
        #Load test data
        reads = pyDNase.BAMHandler(pyDNase.example_reads())
        regions = pyDNase.GenomicIntervalSet(pyDNase.example_regions())
        footprinter = wellington(regions[0],reads)
        #Note - we only check the accuracy of the footprinting to 3 decimal places to allow for differences in floating point numbers
        numpy.testing.assert_array_almost_equal(footprinter.scores.tolist(),[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.8505197962574915, -0.7522459055434079, -0.6405956238609599, -0.35029217770692905, -0.19445213824845226, -0.04510918998207078, -0.013127544708030047, -0.019434755711449096, -0.017813062409838532, -0.4899192539679181, -0.7366170062412767, -1.160234291218491, -1.4932241116142613, -2.528451574312211, -2.9873463332686545, -4.0789439624702215, -4.608073840135845, -4.6080738401358445, -5.46591166889954, -6.317058518040485, -7.846849141309235, -8.70970430615968, -7.84684914298093, -10.57133857477595, -9.524456623200592, -8.450720744685238, -7.351088844276472, -6.227879918162327, -5.085807684913266, -1.412414402021511, -3.461932293846784, -3.6968244901998126, -3.6968244901997713, -3.9374380500569046, -3.9374380500569046, -3.502106381128687, -3.968687434788506, -3.968687434788506, -3.9686874347885044, -4.210084222760481, -4.708248147109799, -4.481083945460659, -4.614616491048433, -6.331304868565458, -6.7188196319447515, -7.805240790859276, -10.096125803164037, -10.096125904865069, -9.804317009970552, -10.942957174739428, -10.831197056706369, -9.451636014876547, -9.271803479479166, -10.547425524609011, -11.356756808330887, -10.173763450595242, -17.266997956146163, -24.135650052599853, -26.79974412054261, -24.068532700189742, -20.83033463447785, -17.442306072203564, -3.3271869067645095, -1.552524387513255, -1.2303389949451933, -1.116146321342096, -0.7241346073398854, -0.8217741198401821, -0.5077397193727583, -0.4619110913457732, -0.22648726483418524, -0.08368942693734599, -0.04662652321248819, -0.10740322088702083, -0.1600382576388667, -0.09849358892510252, -0.2996877100052051, -0.4956516466712493, -0.8286771565689258, -0.7441816651207845, -0.5312102440124086, -6.089145200199429, -54.524611990632465, -55.11290166247622, -53.73358776712574, -56.37380673644542, -59.597668457279916, -63.142121596069494, -69.8245790871056, -76.97479986221292, -83.6326531975367, -88.05928977864403, -87.62205344847811, -90.7846299628178, -94.85120273316905, -90.09506169785546, -85.09363194018195, -90.25622681870428, -80.40916250197246, -84.41195387381595, -96.25001089840575, -105.99203665518576, -109.60076099775432, -116.04973655820825, -124.40507207962382, -120.71820677125163, -121.99289957155713, -121.7696295849731, -128.86709184814546, -130.00197395916774, -138.7286574562139, -150.07398897152254, -141.58993458465335, -134.33745073269844, -134.76596995468543, -106.6912682602024, -96.02214212537493, -85.8950778423277, -73.04392809450209, -54.85091731066348, -44.010732916962205, -31.573437293391223, -23.59371038683095, -18.62378346291484, -3.2863459020700057, -1.8733702431391752, -0.492074167081423, -0.27948577530733343, -0.27948577530733343, -0.07138091975833981, -0.09972653646891905, -0.05418579937724513, -0.024132554170139438, -0.021842812415429565, -0.9566534364564785, -6.932360951667957, -11.187077720714367, -13.553355643835602, -14.21631406001477, -14.983929833667665, -15.422758574896921, -18.32278174888965, -18.2834926735795, -17.265359820713286, -16.13035610465361, -14.086076680349992, -13.521427957090859, -12.515293283803214, -11.480271740126698, -9.92078604101271, -8.797191973771438, -6.985510255611701, -5.426767915467293, -5.183152081566609, -3.7475983370968295, -1.9153547972282414, -0.0006083021245538324, -13.64272847695586, -10.286808471857325, -15.63569341874549, -20.86940117070692, -22.928591109686124, -30.496433497261098, -26.10052633266505, -29.221144392666716, -24.0276270737085, -21.301001754269702, -20.97154340860586, -15.798224427435104, -17.780912132981612, -24.823354886252613, -24.604927499889286, -24.955334454941635, -38.74241644973382, -43.782982787325366, -46.80273522972689, -46.08571305295883, -47.92277577875605, -41.4868217475951, -37.915322367616675, -34.16174895135005, -33.58267055798403, -32.06130865601216, -34.094574908150825, -39.695727106225405, -40.120719852615196, -41.05121481573844, -42.01796136083251, -39.75209693618059, -35.73339613779332, -34.731089314533676, -32.694583271242884, -29.577625993685, -28.026659577292953, -25.215089099008644, -25.174202473704753, -21.952113990014446, -17.028869764873075, -15.578727453806595, -16.1579750791396, -12.974390056172448, -8.418484753962995, -5.7847304546785905, -2.2267773783077134, -1.4570520375724902, -1.543691534890984, -1.575957362444019, -0.7176800307627448, -0.7968619556272615, -4.841045489929452, -5.248527604937139, -1.0472142687516643, -1.0630763089203221, -2.185755905394793, -3.8307492546267254, -4.993169872339857, -7.2764872801107385, -6.792829090234741, -6.452991771598523, -6.952945781664499, -8.215168486202954, -6.613961853070211, -22.150574756810474, -28.514525290020345, -27.33821547951633, -29.034538366843996, -33.82258103970177, -41.26481032907057, -40.912839794048644, -48.684226156049405, -49.44508720397513, -61.863467137712874, -70.11156862148243, -82.93974699146762, -91.62613467860213, -91.54466150389183, -73.5404690802315, -75.77506886003911, -78.05398228595476, -84.42906672420139, -93.01020782082938, -89.65901048860756, -109.20614016921928, -121.0826042903611, -120.2996268556599, -117.38782641714545, -128.50467987996305, -128.9595101418021, -133.14841986541902, -136.82233726671367, -133.94746637928725, -154.5649504690748, -164.11983575086742, -159.85307484109336, -151.89784688535133, -153.56557629402886, -146.72984757341305, -135.04501822595842, -127.92055598311715, -126.08111294376953, -120.03403862241993, -99.25696665821185, -71.19178328684012, -64.94518489350295, -59.98207339614661, -54.12991577221696, -43.206052468123545, -29.456860663206527, -6.411526985333728, -6.44709453786988, -6.215828945120546, -5.762898291384889, -4.3769156224166315, -3.2727915503830047, -2.616087927600661, -2.313254659995694, -1.8641066899878078, -1.8186414374916933, -0.8008712043775049, -0.6426129783652371, -0.5224073311989104, -0.2710345166975603, -0.43819657644966853, -1.2626459311104576, -1.9408301832235342, -3.9812039032702886, -3.9812039032702886, -2.861605777578473, -3.2137507785013066, -3.2137507785013066, -2.9669916392942004, -3.2617340566815645, -3.9686874347885044, -3.54350638697767, -3.54350638697767, -3.1070679887817896, -2.8384054421005627, -2.2611557931086583, -2.9566374983191013, -2.2617270920463315, -2.5370237970085574, -3.2091208219605813, -3.0532448758817448, -1.6966894030794892, -2.2744775410764126, -2.729866824495538, -3.080565957210189, -2.808261821233711, -3.251159821714309, -2.1636899060453407, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],decimal=3)

if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout))