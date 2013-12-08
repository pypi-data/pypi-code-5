# Note: This file was not written for GraTeLPy but is a copy-and-paste
# from this location:
# http://stitchpanorama.sourceforge.net/Python/svd.py

# This file is from Stitch Panorama: A GIMP Plug-In
# http://stitchpanorama.sourceforge.net/
# and the copyright lies with its original author Thomas R. Metcalf.

# Original file begins below this line

# Almost exact translation of the ALGOL SVD algorithm published in
# Numer. Math. 14, 403-420 (1970) by G. H. Golub and C. Reinsch
#
# Copyright (c) 2005 by Thomas R. Metcalf, helicity314-stitch <at> yahoo <dot> com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Pure Python SVD algorithm.
# Input: 2-D list (m by n) with m >= n
# Output: U,W V so that A = U*W*VT
#    Note this program returns V not VT (=transpose(V))
#    On error, a ValueError is raised.
#
# Here is the test case (first example) from Golub and Reinsch
#
# a = [[22.,10., 2.,  3., 7.],
#      [14., 7.,10.,  0., 8.],
#      [-1.,13.,-1.,-11., 3.],
#      [-3.,-2.,13., -2., 4.],
#      [ 9., 8., 1., -2., 4.],
#      [ 9., 1.,-7.,  5.,-1.],
#      [ 2.,-6., 6.,  5., 1.],
#      [ 4., 5., 0., -2., 2.]]
#
# import svd
# import math
# u,w,vt = svd.svd(a)
# print w
#
# [35.327043465311384, 1.2982256062667619e-15,
#  19.999999999999996, 19.595917942265423, 0.0]
#
# the correct answer is (the order may vary)
#
# print (math.sqrt(1248.),20.,math.sqrt(384.),0.,0.)
#
# (35.327043465311391, 20.0, 19.595917942265423, 0.0, 0.0)
#
# transpose and matrix multiplication functions are also included
# to facilitate the solution of linear systems.
#
# Version 1.0 2005 May 01


import copy
import math

def svd(a):
    '''Compute the singular value decomposition of array.'''

    # Golub and Reinsch state that eps should not be smaller than the
    # machine precision, ie the smallest number
    # for which 1+e>1.  tol should be beta/e where beta is the smallest
    # positive number representable in the computer.
    eps = 1.e-15  # assumes double precision
    tol = 1.e-64/eps
    assert 1.0+eps > 1.0 # if this fails, make eps bigger
    assert tol > 0.0     # if this fails, make tol bigger
    itmax = 50
    u = copy.deepcopy(a)
    m = len(a)
    n = len(a[0])
    #if __debug__: print 'a is ',m,' by ',n

    if m < n:
        if __debug__: print 'Error: m is less than n'
        raise ValueError,'SVD Error: m is less than n.'

    e = [0.0]*n  # allocate arrays
    q = [0.0]*n
    v = []
    for k in range(n): v.append([0.0]*n)
 
    # Householder's reduction to bidiagonal form

    g = 0.0
    x = 0.0

    for i in range(n):
        e[i] = g
        s = 0.0
        l = i+1
        for j in range(i,m): s += (u[j][i]*u[j][i])
        if s <= tol:
            g = 0.0
        else:
            f = u[i][i]
            if f < 0.0:
                g = math.sqrt(s)
            else:
                g = -math.sqrt(s)
            h = f*g-s
            u[i][i] = f-g
            for j in range(l,n):
                s = 0.0
                for k in range(i,m): s += u[k][i]*u[k][j]
                f = s/h
                for k in range(i,m): u[k][j] = u[k][j] + f*u[k][i]
        q[i] = g
        s = 0.0
        for j in range(l,n): s = s + u[i][j]*u[i][j]
        if s <= tol:
            g = 0.0
        else:
            f = u[i][i+1]
            if f < 0.0:
                g = math.sqrt(s)
            else:
                g = -math.sqrt(s)
            h = f*g - s
            u[i][i+1] = f-g
            for j in range(l,n): e[j] = u[i][j]/h
            for j in range(l,m):
                s=0.0
                for k in range(l,n): s = s+(u[j][k]*u[i][k])
                for k in range(l,n): u[j][k] = u[j][k]+(s*e[k])
        y = abs(q[i])+abs(e[i])
        if y>x: x=y
    # accumulation of right hand gtransformations
    for i in range(n-1,-1,-1):
        if g != 0.0:
            h = g*u[i][i+1]
            for j in range(l,n): v[j][i] = u[i][j]/h
            for j in range(l,n):
                s=0.0
                for k in range(l,n): s += (u[i][k]*v[k][j])
                for k in range(l,n): v[k][j] += (s*v[k][i])
        for j in range(l,n):
            v[i][j] = 0.0
            v[j][i] = 0.0
        v[i][i] = 1.0
        g = e[i]
        l = i
    #accumulation of left hand transformations
    for i in range(n-1,-1,-1):
        l = i+1
        g = q[i]
        for j in range(l,n): u[i][j] = 0.0
        if g != 0.0:
            h = u[i][i]*g
            for j in range(l,n):
                s=0.0
                for k in range(l,m): s += (u[k][i]*u[k][j])
                f = s/h
                for k in range(i,m): u[k][j] += (f*u[k][i])
            for j in range(i,m): u[j][i] = u[j][i]/g
        else:
            for j in range(i,m): u[j][i] = 0.0
        u[i][i] += 1.0
    #diagonalization of the bidiagonal form
    eps = eps*x
    for k in range(n-1,-1,-1):
        for iteration in range(itmax):
            # test f splitting
            for l in range(k,-1,-1):
                goto_test_f_convergence = False
                if abs(e[l]) <= eps:
                    # goto test f convergence
                    goto_test_f_convergence = True
                    break  # break out of l loop
                if abs(q[l-1]) <= eps:
                    # goto cancellation
                    break  # break out of l loop
            if not goto_test_f_convergence:
                #cancellation of e[l] if l>0
                c = 0.0
                s = 1.0
                l1 = l-1
                for i in range(l,k+1):
                    f = s*e[i]
                    e[i] = c*e[i]
                    if abs(f) <= eps:
                        #goto test f convergence
                        break
                    g = q[i]
                    h = pythag(f,g)
                    q[i] = h
                    c = g/h
                    s = -f/h
                    for j in range(m):
                        y = u[j][l1]
                        z = u[j][i]
                        u[j][l1] = y*c+z*s
                        u[j][i] = -y*s+z*c
            # test f convergence
            z = q[k]
            if l == k:
                # convergence
                if z<0.0:
                    #q[k] is made non-negative
                    q[k] = -z
                    for j in range(n):
                        v[j][k] = -v[j][k]
                break  # break out of iteration loop and move on to next k value
            if iteration >= itmax-1:
                if __debug__: print 'Error: no convergence.'
                # should this move on the the next k or exit with error??
                #raise ValueError,'SVD Error: No convergence.'  # exit the program with error
                break  # break out of iteration loop and move on to next k
            # shift from bottom 2x2 minor
            x = q[l]
            y = q[k-1]
            g = e[k-1]
            h = e[k]
            f = ((y-z)*(y+z)+(g-h)*(g+h))/(2.0*h*y)
            g = pythag(f,1.0)
            if f < 0:
                f = ((x-z)*(x+z)+h*(y/(f-g)-h))/x
            else:
                f = ((x-z)*(x+z)+h*(y/(f+g)-h))/x
            # next QR transformation
            c = 1.0
            s = 1.0
            for i in range(l+1,k+1):
                g = e[i]
                y = q[i]
                h = s*g
                g = c*g
                z = pythag(f,h)
                e[i-1] = z
                c = f/z
                s = h/z
                f = x*c+g*s
                g = -x*s+g*c
                h = y*s
                y = y*c
                for j in range(n):
                    x = v[j][i-1]
                    z = v[j][i]
                    v[j][i-1] = x*c+z*s
                    v[j][i] = -x*s+z*c
                z = pythag(f,h)
                q[i-1] = z
                c = f/z
                s = h/z
                f = c*g+s*y
                x = -s*g+c*y
                for j in range(m):
                    y = u[j][i-1]
                    z = u[j][i]
                    u[j][i-1] = y*c+z*s
                    u[j][i] = -y*s+z*c
            e[l] = 0.0
            e[k] = f
            q[k] = x
            # goto test f splitting
        
            
    #vt = transpose(v)
    #return (u,q,vt)
    return (u,q,v)

def pythag(a,b):
    absa = abs(a)
    absb = abs(b)
    if absa > absb: return absa*math.sqrt(1.0+(absb/absa)**2)
    else:
        if absb == 0.0: return 0.0
        else: return absb*math.sqrt(1.0+(absa/absb)**2)

def transpose(a):
    '''Compute the transpose of a matrix.'''
    m = len(a)
    n = len(a[0])
    at = []
    for i in range(n): at.append([0.0]*m)
    for i in range(m):
        for j in range(n):
            at[j][i]=a[i][j]
    return at

def matrixmultiply(a,b):
    '''Multiply two matrices.
    a must be two dimensional
    b can be one or two dimensional.'''
    
    am = len(a)
    bm = len(b)
    an = len(a[0])
    try:
        bn = len(b[0])
    except TypeError:
        bn = 1
    if an != bm:
        raise ValueError, 'matrixmultiply error: array sizes do not match.'
    cm = am
    cn = bn
    if bn == 1:
        c = [0.0]*cm
    else:
        c = []
        for k in range(cm): c.append([0.0]*cn)
    for i in range(cm):
        for j in range(cn):
            for k in range(an):
                if bn == 1:
                    c[i] += a[i][k]*b[k]
                else:
                    c[i][j] += a[i][k]*b[k][j]
    
    return c
 
## 		    GNU GENERAL PUBLIC LICENSE
## 		       Version 2, June 1991

##  Copyright (C) 1989, 1991 Free Software Foundation, Inc.
##                        59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##  Everyone is permitted to copy and distribute verbatim copies
##  of this license document, but changing it is not allowed.

## 			    Preamble

##   The licenses for most software are designed to take away your
## freedom to share and change it.  By contrast, the GNU General Public
## License is intended to guarantee your freedom to share and change free
## software--to make sure the software is free for all its users.  This
## General Public License applies to most of the Free Software
## Foundation's software and to any other program whose authors commit to
## using it.  (Some other Free Software Foundation software is covered by
## the GNU Library General Public License instead.)  You can apply it to
## your programs, too.

##   When we speak of free software, we are referring to freedom, not
## price.  Our General Public Licenses are designed to make sure that you
## have the freedom to distribute copies of free software (and charge for
## this service if you wish), that you receive source code or can get it
## if you want it, that you can change the software or use pieces of it
## in new free programs; and that you know you can do these things.

##   To protect your rights, we need to make restrictions that forbid
## anyone to deny you these rights or to ask you to surrender the rights.
## These restrictions translate to certain responsibilities for you if you
## distribute copies of the software, or if you modify it.

##   For example, if you distribute copies of such a program, whether
## gratis or for a fee, you must give the recipients all the rights that
## you have.  You must make sure that they, too, receive or can get the
## source code.  And you must show them these terms so they know their
## rights.

##   We protect your rights with two steps: (1) copyright the software, and
## (2) offer you this license which gives you legal permission to copy,
## distribute and/or modify the software.

##   Also, for each author's protection and ours, we want to make certain
## that everyone understands that there is no warranty for this free
## software.  If the software is modified by someone else and passed on, we
## want its recipients to know that what they have is not the original, so
## that any problems introduced by others will not reflect on the original
## authors' reputations.

##   Finally, any free program is threatened constantly by software
## patents.  We wish to avoid the danger that redistributors of a free
## program will individually obtain patent licenses, in effect making the
## program proprietary.  To prevent this, we have made it clear that any
## patent must be licensed for everyone's free use or not licensed at all.

##   The precise terms and conditions for copying, distribution and
## modification follow.
## 
## 		    GNU GENERAL PUBLIC LICENSE
##    TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

##   0. This License applies to any program or other work which contains
## a notice placed by the copyright holder saying it may be distributed
## under the terms of this General Public License.  The "Program", below,
## refers to any such program or work, and a "work based on the Program"
## means either the Program or any derivative work under copyright law:
## that is to say, a work containing the Program or a portion of it,
## either verbatim or with modifications and/or translated into another
## language.  (Hereinafter, translation is included without limitation in
## the term "modification".)  Each licensee is addressed as "you".

## Activities other than copying, distribution and modification are not
## covered by this License; they are outside its scope.  The act of
## running the Program is not restricted, and the output from the Program
## is covered only if its contents constitute a work based on the
## Program (independent of having been made by running the Program).
## Whether that is true depends on what the Program does.

##   1. You may copy and distribute verbatim copies of the Program's
## source code as you receive it, in any medium, provided that you
## conspicuously and appropriately publish on each copy an appropriate
## copyright notice and disclaimer of warranty; keep intact all the
## notices that refer to this License and to the absence of any warranty;
## and give any other recipients of the Program a copy of this License
## along with the Program.

## You may charge a fee for the physical act of transferring a copy, and
## you may at your option offer warranty protection in exchange for a fee.

##   2. You may modify your copy or copies of the Program or any portion
## of it, thus forming a work based on the Program, and copy and
## distribute such modifications or work under the terms of Section 1
## above, provided that you also meet all of these conditions:

##     a) You must cause the modified files to carry prominent notices
##     stating that you changed the files and the date of any change.

##     b) You must cause any work that you distribute or publish, that in
##     whole or in part contains or is derived from the Program or any
##     part thereof, to be licensed as a whole at no charge to all third
##     parties under the terms of this License.

##     c) If the modified program normally reads commands interactively
##     when run, you must cause it, when started running for such
##     interactive use in the most ordinary way, to print or display an
##     announcement including an appropriate copyright notice and a
##     notice that there is no warranty (or else, saying that you provide
##     a warranty) and that users may redistribute the program under
##     these conditions, and telling the user how to view a copy of this
##     License.  (Exception: if the Program itself is interactive but
##     does not normally print such an announcement, your work based on
##     the Program is not required to print an announcement.)
## 
## These requirements apply to the modified work as a whole.  If
## identifiable sections of that work are not derived from the Program,
## and can be reasonably considered independent and separate works in
## themselves, then this License, and its terms, do not apply to those
## sections when you distribute them as separate works.  But when you
## distribute the same sections as part of a whole which is a work based
## on the Program, the distribution of the whole must be on the terms of
## this License, whose permissions for other licensees extend to the
## entire whole, and thus to each and every part regardless of who wrote it.

## Thus, it is not the intent of this section to claim rights or contest
## your rights to work written entirely by you; rather, the intent is to
## exercise the right to control the distribution of derivative or
## collective works based on the Program.

## In addition, mere aggregation of another work not based on the Program
## with the Program (or with a work based on the Program) on a volume of
## a storage or distribution medium does not bring the other work under
## the scope of this License.

##   3. You may copy and distribute the Program (or a work based on it,
## under Section 2) in object code or executable form under the terms of
## Sections 1 and 2 above provided that you also do one of the following:

##     a) Accompany it with the complete corresponding machine-readable
##     source code, which must be distributed under the terms of Sections
##     1 and 2 above on a medium customarily used for software interchange; or,

##     b) Accompany it with a written offer, valid for at least three
##     years, to give any third party, for a charge no more than your
##     cost of physically performing source distribution, a complete
##     machine-readable copy of the corresponding source code, to be
##     distributed under the terms of Sections 1 and 2 above on a medium
##     customarily used for software interchange; or,

##     c) Accompany it with the information you received as to the offer
##     to distribute corresponding source code.  (This alternative is
##     allowed only for noncommercial distribution and only if you
##     received the program in object code or executable form with such
##     an offer, in accord with Subsection b above.)

## The source code for a work means the preferred form of the work for
## making modifications to it.  For an executable work, complete source
## code means all the source code for all modules it contains, plus any
## associated interface definition files, plus the scripts used to
## control compilation and installation of the executable.  However, as a
## special exception, the source code distributed need not include
## anything that is normally distributed (in either source or binary
## form) with the major components (compiler, kernel, and so on) of the
## operating system on which the executable runs, unless that component
## itself accompanies the executable.

## If distribution of executable or object code is made by offering
## access to copy from a designated place, then offering equivalent
## access to copy the source code from the same place counts as
## distribution of the source code, even though third parties are not
## compelled to copy the source along with the object code.
## 
##   4. You may not copy, modify, sublicense, or distribute the Program
## except as expressly provided under this License.  Any attempt
## otherwise to copy, modify, sublicense or distribute the Program is
## void, and will automatically terminate your rights under this License.
## However, parties who have received copies, or rights, from you under
## this License will not have their licenses terminated so long as such
## parties remain in full compliance.

##   5. You are not required to accept this License, since you have not
## signed it.  However, nothing else grants you permission to modify or
## distribute the Program or its derivative works.  These actions are
## prohibited by law if you do not accept this License.  Therefore, by
## modifying or distributing the Program (or any work based on the
## Program), you indicate your acceptance of this License to do so, and
## all its terms and conditions for copying, distributing or modifying
## the Program or works based on it.

##   6. Each time you redistribute the Program (or any work based on the
## Program), the recipient automatically receives a license from the
## original licensor to copy, distribute or modify the Program subject to
## these terms and conditions.  You may not impose any further
## restrictions on the recipients' exercise of the rights granted herein.
## You are not responsible for enforcing compliance by third parties to
## this License.

##   7. If, as a consequence of a court judgment or allegation of patent
## infringement or for any other reason (not limited to patent issues),
## conditions are imposed on you (whether by court order, agreement or
## otherwise) that contradict the conditions of this License, they do not
## excuse you from the conditions of this License.  If you cannot
## distribute so as to satisfy simultaneously your obligations under this
## License and any other pertinent obligations, then as a consequence you
## may not distribute the Program at all.  For example, if a patent
## license would not permit royalty-free redistribution of the Program by
## all those who receive copies directly or indirectly through you, then
## the only way you could satisfy both it and this License would be to
## refrain entirely from distribution of the Program.

## If any portion of this section is held invalid or unenforceable under
## any particular circumstance, the balance of the section is intended to
## apply and the section as a whole is intended to apply in other
## circumstances.

## It is not the purpose of this section to induce you to infringe any
## patents or other property right claims or to contest validity of any
## such claims; this section has the sole purpose of protecting the
## integrity of the free software distribution system, which is
## implemented by public license practices.  Many people have made
## generous contributions to the wide range of software distributed
## through that system in reliance on consistent application of that
## system; it is up to the author/donor to decide if he or she is willing
## to distribute software through any other system and a licensee cannot
## impose that choice.

## This section is intended to make thoroughly clear what is believed to
## be a consequence of the rest of this License.
## 
##   8. If the distribution and/or use of the Program is restricted in
## certain countries either by patents or by copyrighted interfaces, the
## original copyright holder who places the Program under this License
## may add an explicit geographical distribution limitation excluding
## those countries, so that distribution is permitted only in or among
## countries not thus excluded.  In such case, this License incorporates
## the limitation as if written in the body of this License.

##   9. The Free Software Foundation may publish revised and/or new versions
## of the General Public License from time to time.  Such new versions will
## be similar in spirit to the present version, but may differ in detail to
## address new problems or concerns.

## Each version is given a distinguishing version number.  If the Program
## specifies a version number of this License which applies to it and "any
## later version", you have the option of following the terms and conditions
## either of that version or of any later version published by the Free
## Software Foundation.  If the Program does not specify a version number of
## this License, you may choose any version ever published by the Free Software
## Foundation.

##   10. If you wish to incorporate parts of the Program into other free
## programs whose distribution conditions are different, write to the author
## to ask for permission.  For software which is copyrighted by the Free
## Software Foundation, write to the Free Software Foundation; we sometimes
## make exceptions for this.  Our decision will be guided by the two goals
## of preserving the free status of all derivatives of our free software and
## of promoting the sharing and reuse of software generally.

## 			    NO WARRANTY

##   11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
## FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
## OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
## PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
## OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
## MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
## TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
## PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
## REPAIR OR CORRECTION.

##   12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
## WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
## REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
## INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
## OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
## TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
## YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
## PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGES.

## 		     END OF TERMS AND CONDITIONS
## 
