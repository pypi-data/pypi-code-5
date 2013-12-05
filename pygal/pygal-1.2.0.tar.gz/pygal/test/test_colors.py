from pygal.colors import (
    rgb_to_hsl, hsl_to_rgb, darken, lighten, saturate, desaturate, rotate)


def test_darken():
    assert darken('#800', 20) == '#220000'
    assert darken('#800', 0) == '#880000'
    assert darken('#ffffff', 10) == '#e6e6e6'
    assert darken('#000000', 10) == '#000000'
    assert darken('#f3148a', 25) == '#810747'
    assert darken('#121212', 1) == '#0f0f0f'
    assert darken('#999999', 100) == '#000000'
    assert darken('#1479ac', 8) == '#105f87'


def test_lighten():
    assert lighten('#800', 20) == '#ee0000'
    assert lighten('#800', 0) == '#880000'
    assert lighten('#ffffff', 10) == '#ffffff'
    assert lighten('#000000', 10) == '#1a1a1a'
    assert lighten('#f3148a', 25) == '#f98dc6'
    assert lighten('#121212', 1) == '#151515'
    assert lighten('#999999', 100) == '#ffffff'
    assert lighten('#1479ac', 8) == '#1893d1'


def test_saturate():
    assert saturate('#000', 20) == '#000000'
    assert saturate('#fff', 20) == '#ffffff'
    assert saturate('#8a8', 100) == '#33ff33'
    assert saturate('#855', 20) == '#9e3f3f'


def test_desaturate():
    assert desaturate('#000', 20) == '#000000'
    assert desaturate('#fff', 20) == '#ffffff'
    assert desaturate('#8a8', 100) == '#999999'
    assert desaturate('#855', 20) == '#726b6b'


def test_rotate():
    assert rotate('#000', 45) == '#000000'
    assert rotate('#fff', 45) == '#ffffff'
    assert rotate('#811', 45) == '#886a11'
    assert rotate('#8a8', 360) == '#88aa88'
    assert rotate('#8a8', 0) == '#88aa88'
    assert rotate('#8a8', -360) == '#88aa88'


def test_hsl_to_rgb_part_0():
    assert hsl_to_rgb(0, 100, 50) == (255, 0, 0)
    assert hsl_to_rgb(60, 100, 50) == (255, 255, 0)
    assert hsl_to_rgb(120, 100, 50) == (0, 255, 0)
    assert hsl_to_rgb(180, 100, 50) == (0, 255, 255)
    assert hsl_to_rgb(240, 100, 50) == (0, 0, 255)
    assert hsl_to_rgb(300, 100, 50) == (255, 0, 255)


def test_rgb_to_hsl_part_0():
    assert rgb_to_hsl(255, 0, 0) == (0, 100, 50)
    assert rgb_to_hsl(255, 255, 0) == (60, 100, 50)
    assert rgb_to_hsl(0, 255, 0) == (120, 100, 50)
    assert rgb_to_hsl(0, 255, 255) == (180, 100, 50)
    assert rgb_to_hsl(0, 0, 255) == (240, 100, 50)
    assert rgb_to_hsl(255, 0, 255) == (300, 100, 50)


def test_hsl_to_rgb_part_1():
    assert hsl_to_rgb(-360, 100, 50) == (255, 0, 0)
    assert hsl_to_rgb(-300, 100, 50) == (255, 255, 0)
    assert hsl_to_rgb(-240, 100, 50) == (0, 255, 0)
    assert hsl_to_rgb(-180, 100, 50) == (0, 255, 255)
    assert hsl_to_rgb(-120, 100, 50) == (0, 0, 255)
    assert hsl_to_rgb(-60, 100, 50) == (255, 0, 255)


def test_rgb_to_hsl_part_1():
    # assert rgb_to_hsl(255, 0, 0) == (-360, 100, 50)
    # assert rgb_to_hsl(255, 255, 0) == (-300, 100, 50)
    # assert rgb_to_hsl(0, 255, 0) == (-240, 100, 50)
    # assert rgb_to_hsl(0, 255, 255) == (-180, 100, 50)
    # assert rgb_to_hsl(0, 0, 255) == (-120, 100, 50)
    # assert rgb_to_hsl(255, 0, 255) == (-60, 100, 50)
    pass


def test_hsl_to_rgb_part_2():
    assert hsl_to_rgb(360, 100, 50) == (255, 0, 0)
    assert hsl_to_rgb(420, 100, 50) == (255, 255, 0)
    assert hsl_to_rgb(480, 100, 50) == (0, 255, 0)
    assert hsl_to_rgb(540, 100, 50) == (0, 255, 255)
    assert hsl_to_rgb(600, 100, 50) == (0, 0, 255)
    assert hsl_to_rgb(660, 100, 50) == (255, 0, 255)


def test_rgb_to_hsl_part_2():
    # assert rgb_to_hsl(255, 0, 0) == (360, 100, 50)
    # assert rgb_to_hsl(255, 255, 0) == (420, 100, 50)
    # assert rgb_to_hsl(0, 255, 0) == (480, 100, 50)
    # assert rgb_to_hsl(0, 255, 255) == (540, 100, 50)
    # assert rgb_to_hsl(0, 0, 255) == (600, 100, 50)
    # assert rgb_to_hsl(255, 0, 255) == (660, 100, 50)
    pass


def test_hsl_to_rgb_part_3():
    assert hsl_to_rgb(6120, 100, 50) == (255, 0, 0)
    assert hsl_to_rgb(-9660, 100, 50) == (255, 255, 0)
    assert hsl_to_rgb(99840, 100, 50) == (0, 255, 0)
    assert hsl_to_rgb(-900, 100, 50) == (0, 255, 255)
    assert hsl_to_rgb(-104880, 100, 50) == (0, 0, 255)
    assert hsl_to_rgb(2820, 100, 50) == (255, 0, 255)


def test_rgb_to_hsl_part_3():
    # assert rgb_to_hsl(255, 0, 0) == (6120, 100, 50)
    # assert rgb_to_hsl(255, 255, 0) == (-9660, 100, 50)
    # assert rgb_to_hsl(0, 255, 0) == (99840, 100, 50)
    # assert rgb_to_hsl(0, 255, 255) == (-900, 100, 50)
    # assert rgb_to_hsl(0, 0, 255) == (-104880, 100, 50)
    # assert rgb_to_hsl(255, 0, 255) == (2820, 100, 50)
    pass


def test_hsl_to_rgb_part_4():
    assert hsl_to_rgb(0, 100, 50) == (255, 0, 0)
    assert hsl_to_rgb(12, 100, 50) == (255, 51, 0)
    assert hsl_to_rgb(24, 100, 50) == (255, 102, 0)
    assert hsl_to_rgb(36, 100, 50) == (255, 153, 0)
    assert hsl_to_rgb(48, 100, 50) == (255, 204, 0)
    assert hsl_to_rgb(60, 100, 50) == (255, 255, 0)
    assert hsl_to_rgb(72, 100, 50) == (204, 255, 0)
    assert hsl_to_rgb(84, 100, 50) == (153, 255, 0)
    assert hsl_to_rgb(96, 100, 50) == (102, 255, 0)
    assert hsl_to_rgb(108, 100, 50) == (51, 255, 0)
    assert hsl_to_rgb(120, 100, 50) == (0, 255, 0)


def test_rgb_to_hsl_part_4():
    assert rgb_to_hsl(255, 0, 0) == (0, 100, 50)
    assert rgb_to_hsl(255, 51, 0) == (12, 100, 50)
    assert rgb_to_hsl(255, 102, 0) == (24, 100, 50)
    assert rgb_to_hsl(255, 153, 0) == (36, 100, 50)
    assert rgb_to_hsl(255, 204, 0) == (48, 100, 50)
    assert rgb_to_hsl(255, 255, 0) == (60, 100, 50)
    assert rgb_to_hsl(204, 255, 0) == (72, 100, 50)
    assert rgb_to_hsl(153, 255, 0) == (84, 100, 50)
    assert rgb_to_hsl(102, 255, 0) == (96, 100, 50)
    assert rgb_to_hsl(51, 255, 0) == (108, 100, 50)
    assert rgb_to_hsl(0, 255, 0) == (120, 100, 50)


def test_hsl_to_rgb_part_5():
    assert hsl_to_rgb(120, 100, 50) == (0, 255, 0)
    assert hsl_to_rgb(132, 100, 50) == (0, 255, 51)
    assert hsl_to_rgb(144, 100, 50) == (0, 255, 102)
    assert hsl_to_rgb(156, 100, 50) == (0, 255, 153)
    assert hsl_to_rgb(168, 100, 50) == (0, 255, 204)
    assert hsl_to_rgb(180, 100, 50) == (0, 255, 255)
    assert hsl_to_rgb(192, 100, 50) == (0, 204, 255)
    assert hsl_to_rgb(204, 100, 50) == (0, 153, 255)
    assert hsl_to_rgb(216, 100, 50) == (0, 102, 255)
    assert hsl_to_rgb(228, 100, 50) == (0, 51, 255)
    assert hsl_to_rgb(240, 100, 50) == (0, 0, 255)


def test_rgb_to_hsl_part_5():
    assert rgb_to_hsl(0, 255, 0) == (120, 100, 50)
    assert rgb_to_hsl(0, 255, 51) == (132, 100, 50)
    assert rgb_to_hsl(0, 255, 102) == (144, 100, 50)
    assert rgb_to_hsl(0, 255, 153) == (156, 100, 50)
    assert rgb_to_hsl(0, 255, 204) == (168, 100, 50)
    assert rgb_to_hsl(0, 255, 255) == (180, 100, 50)
    assert rgb_to_hsl(0, 204, 255) == (192, 100, 50)
    assert rgb_to_hsl(0, 153, 255) == (204, 100, 50)
    assert rgb_to_hsl(0, 102, 255) == (216, 100, 50)
    assert rgb_to_hsl(0, 51, 255) == (228, 100, 50)
    assert rgb_to_hsl(0, 0, 255) == (240, 100, 50)


def test_hsl_to_rgb_part_6():
    assert hsl_to_rgb(240, 100, 50) == (0, 0, 255)
    assert hsl_to_rgb(252, 100, 50) == (51, 0, 255)
    assert hsl_to_rgb(264, 100, 50) == (102, 0, 255)
    assert hsl_to_rgb(276, 100, 50) == (153, 0, 255)
    assert hsl_to_rgb(288, 100, 50) == (204, 0, 255)
    assert hsl_to_rgb(300, 100, 50) == (255, 0, 255)
    assert hsl_to_rgb(312, 100, 50) == (255, 0, 204)
    assert hsl_to_rgb(324, 100, 50) == (255, 0, 153)
    assert hsl_to_rgb(336, 100, 50) == (255, 0, 102)
    assert hsl_to_rgb(348, 100, 50) == (255, 0, 51)
    assert hsl_to_rgb(360, 100, 50) == (255, 0, 0)


def test_rgb_to_hsl_part_6():
    assert rgb_to_hsl(0, 0, 255) == (240, 100, 50)
    assert rgb_to_hsl(51, 0, 255) == (252, 100, 50)
    assert rgb_to_hsl(102, 0, 255) == (264, 100, 50)
    assert rgb_to_hsl(153, 0, 255) == (276, 100, 50)
    assert rgb_to_hsl(204, 0, 255) == (288, 100, 50)
    assert rgb_to_hsl(255, 0, 255) == (300, 100, 50)
    assert rgb_to_hsl(255, 0, 204) == (312, 100, 50)
    assert rgb_to_hsl(255, 0, 153) == (324, 100, 50)
    assert rgb_to_hsl(255, 0, 102) == (336, 100, 50)
    assert rgb_to_hsl(255, 0, 51) == (348, 100, 50)
    # assert rgb_to_hsl(255, 0, 0) == (360, 100, 50)


def test_hsl_to_rgb_part_7():
    assert hsl_to_rgb(0, 20, 50) == (153, 102, 102)
    assert hsl_to_rgb(0, 60, 50) == (204, 51, 51)
    assert hsl_to_rgb(0, 100, 50) == (255, 0, 0)


def test_rgb_to_hsl_part_7():
    assert rgb_to_hsl(153, 102, 102) == (0, 20, 50)
    assert rgb_to_hsl(204, 51, 51) == (0, 60, 50)
    assert rgb_to_hsl(255, 0, 0) == (0, 100, 50)


def test_hsl_to_rgb_part_8():
    assert hsl_to_rgb(60, 20, 50) == (153, 153, 102)
    assert hsl_to_rgb(60, 60, 50) == (204, 204, 51)
    assert hsl_to_rgb(60, 100, 50) == (255, 255, 0)


def test_rgb_to_hsl_part_8():
    assert rgb_to_hsl(153, 153, 102) == (60, 20, 50)
    assert rgb_to_hsl(204, 204, 51) == (60, 60, 50)
    assert rgb_to_hsl(255, 255, 0) == (60, 100, 50)


def test_hsl_to_rgb_part_9():
    assert hsl_to_rgb(120, 20, 50) == (102, 153, 102)
    assert hsl_to_rgb(120, 60, 50) == (51, 204, 51)
    assert hsl_to_rgb(120, 100, 50) == (0, 255, 0)


def test_rgb_to_hsl_part_9():
    assert rgb_to_hsl(102, 153, 102) == (120, 20, 50)
    assert rgb_to_hsl(51, 204, 51) == (120, 60, 50)
    assert rgb_to_hsl(0, 255, 0) == (120, 100, 50)


def test_hsl_to_rgb_part_10():
    assert hsl_to_rgb(180, 20, 50) == (102, 153, 153)
    assert hsl_to_rgb(180, 60, 50) == (51, 204, 204)
    assert hsl_to_rgb(180, 100, 50) == (0, 255, 255)


def test_rgb_to_hsl_part_10():
    assert rgb_to_hsl(102, 153, 153) == (180, 20, 50)
    assert rgb_to_hsl(51, 204, 204) == (180, 60, 50)
    assert rgb_to_hsl(0, 255, 255) == (180, 100, 50)


def test_hsl_to_rgb_part_11():
    assert hsl_to_rgb(240, 20, 50) == (102, 102, 153)
    assert hsl_to_rgb(240, 60, 50) == (51, 51, 204)
    assert hsl_to_rgb(240, 100, 50) == (0, 0, 255)


def test_rgb_to_hsl_part_11():
    assert rgb_to_hsl(102, 102, 153) == (240, 20, 50)
    assert rgb_to_hsl(51, 51, 204) == (240, 60, 50)
    assert rgb_to_hsl(0, 0, 255) == (240, 100, 50)


def test_hsl_to_rgb_part_12():
    assert hsl_to_rgb(300, 20, 50) == (153, 102, 153)
    assert hsl_to_rgb(300, 60, 50) == (204, 51, 204)
    assert hsl_to_rgb(300, 100, 50) == (255, 0, 255)


def test_rgb_to_hsl_part_12():
    assert rgb_to_hsl(153, 102, 153) == (300, 20, 50)
    assert rgb_to_hsl(204, 51, 204) == (300, 60, 50)
    assert rgb_to_hsl(255, 0, 255) == (300, 100, 50)


def test_hsl_to_rgb_part_13():
    assert hsl_to_rgb(0, 100, 0) == (0, 0, 0)
    assert hsl_to_rgb(0, 100, 10) == (51, 0, 0)
    assert hsl_to_rgb(0, 100, 20) == (102, 0, 0)
    assert hsl_to_rgb(0, 100, 30) == (153, 0, 0)
    assert hsl_to_rgb(0, 100, 40) == (204, 0, 0)
    assert hsl_to_rgb(0, 100, 50) == (255, 0, 0)
    assert hsl_to_rgb(0, 100, 60) == (255, 51, 51)
    assert hsl_to_rgb(0, 100, 70) == (255, 102, 102)
    assert hsl_to_rgb(0, 100, 80) == (255, 153, 153)
    assert hsl_to_rgb(0, 100, 90) == (255, 204, 204)
    assert hsl_to_rgb(0, 100, 100) == (255, 255, 255)


def test_rgb_to_hsl_part_13():
    assert rgb_to_hsl(0, 0, 0) == (0, 0, 0)
    assert rgb_to_hsl(51, 0, 0) == (0, 100, 10)
    assert rgb_to_hsl(102, 0, 0) == (0, 100, 20)
    assert rgb_to_hsl(153, 0, 0) == (0, 100, 30)
    assert rgb_to_hsl(204, 0, 0) == (0, 100, 40)
    assert rgb_to_hsl(255, 0, 0) == (0, 100, 50)
    assert rgb_to_hsl(255, 51, 51) == (0, 100, 60)
    assert rgb_to_hsl(255, 102, 102) == (0, 100, 70)
    assert rgb_to_hsl(255, 153, 153) == (0, 100, 80)
    assert rgb_to_hsl(255, 204, 204) == (0, 100, 90)
    assert rgb_to_hsl(255, 255, 255) == (0, 0, 100)


def test_hsl_to_rgb_part_14():
    assert hsl_to_rgb(60, 100, 0) == (0, 0, 0)
    assert hsl_to_rgb(60, 100, 10) == (51, 51, 0)
    assert hsl_to_rgb(60, 100, 20) == (102, 102, 0)
    assert hsl_to_rgb(60, 100, 30) == (153, 153, 0)
    assert hsl_to_rgb(60, 100, 40) == (204, 204, 0)
    assert hsl_to_rgb(60, 100, 50) == (255, 255, 0)
    assert hsl_to_rgb(60, 100, 60) == (255, 255, 51)
    assert hsl_to_rgb(60, 100, 70) == (255, 255, 102)
    assert hsl_to_rgb(60, 100, 80) == (255, 255, 153)
    assert hsl_to_rgb(60, 100, 90) == (255, 255, 204)
    assert hsl_to_rgb(60, 100, 100) == (255, 255, 255)


def test_rgb_to_hsl_part_14():
    # assert rgb_to_hsl(0, 0, 0) == (60, 100, 0)
    assert rgb_to_hsl(51, 51, 0) == (60, 100, 10)
    assert rgb_to_hsl(102, 102, 0) == (60, 100, 20)
    assert rgb_to_hsl(153, 153, 0) == (60, 100, 30)
    assert rgb_to_hsl(204, 204, 0) == (60, 100, 40)
    assert rgb_to_hsl(255, 255, 0) == (60, 100, 50)
    assert rgb_to_hsl(255, 255, 51) == (60, 100, 60)
    assert rgb_to_hsl(255, 255, 102) == (60, 100, 70)
    assert rgb_to_hsl(255, 255, 153) == (60, 100, 80)
    assert rgb_to_hsl(255, 255, 204) == (60, 100, 90)
    # assert rgb_to_hsl(255, 255, 255) == (60, 100, 100)


def test_hsl_to_rgb_part_15():
    assert hsl_to_rgb(120, 100, 0) == (0, 0, 0)
    assert hsl_to_rgb(120, 100, 10) == (0, 51, 0)
    assert hsl_to_rgb(120, 100, 20) == (0, 102, 0)
    assert hsl_to_rgb(120, 100, 30) == (0, 153, 0)
    assert hsl_to_rgb(120, 100, 40) == (0, 204, 0)
    assert hsl_to_rgb(120, 100, 50) == (0, 255, 0)
    assert hsl_to_rgb(120, 100, 60) == (51, 255, 51)
    assert hsl_to_rgb(120, 100, 70) == (102, 255, 102)
    assert hsl_to_rgb(120, 100, 80) == (153, 255, 153)
    assert hsl_to_rgb(120, 100, 90) == (204, 255, 204)
    assert hsl_to_rgb(120, 100, 100) == (255, 255, 255)


def test_rgb_to_hsl_part_15():
    # assert rgb_to_hsl(0, 0, 0) == (120, 100, 0)
    assert rgb_to_hsl(0, 51, 0) == (120, 100, 10)
    assert rgb_to_hsl(0, 102, 0) == (120, 100, 20)
    assert rgb_to_hsl(0, 153, 0) == (120, 100, 30)
    assert rgb_to_hsl(0, 204, 0) == (120, 100, 40)
    assert rgb_to_hsl(0, 255, 0) == (120, 100, 50)
    assert rgb_to_hsl(51, 255, 51) == (120, 100, 60)
    assert rgb_to_hsl(102, 255, 102) == (120, 100, 70)
    assert rgb_to_hsl(153, 255, 153) == (120, 100, 80)
    assert rgb_to_hsl(204, 255, 204) == (120, 100, 90)
    # assert rgb_to_hsl(255, 255, 255) == (120, 100, 100)


def test_hsl_to_rgb_part_16():
    assert hsl_to_rgb(180, 100, 0) == (0, 0, 0)
    assert hsl_to_rgb(180, 100, 10) == (0, 51, 51)
    assert hsl_to_rgb(180, 100, 20) == (0, 102, 102)
    assert hsl_to_rgb(180, 100, 30) == (0, 153, 153)
    assert hsl_to_rgb(180, 100, 40) == (0, 204, 204)
    assert hsl_to_rgb(180, 100, 50) == (0, 255, 255)
    assert hsl_to_rgb(180, 100, 60) == (51, 255, 255)
    assert hsl_to_rgb(180, 100, 70) == (102, 255, 255)
    assert hsl_to_rgb(180, 100, 80) == (153, 255, 255)
    assert hsl_to_rgb(180, 100, 90) == (204, 255, 255)
    assert hsl_to_rgb(180, 100, 100) == (255, 255, 255)


def test_rgb_to_hsl_part_16():
    # assert rgb_to_hsl(0, 0, 0) == (180, 100, 0)
    assert rgb_to_hsl(0, 51, 51) == (180, 100, 10)
    assert rgb_to_hsl(0, 102, 102) == (180, 100, 20)
    assert rgb_to_hsl(0, 153, 153) == (180, 100, 30)
    assert rgb_to_hsl(0, 204, 204) == (180, 100, 40)
    assert rgb_to_hsl(0, 255, 255) == (180, 100, 50)
    assert rgb_to_hsl(51, 255, 255) == (180, 100, 60)
    assert rgb_to_hsl(102, 255, 255) == (180, 100, 70)
    assert rgb_to_hsl(153, 255, 255) == (180, 100, 80)
    assert rgb_to_hsl(204, 255, 255) == (180, 100, 90)
    # assert rgb_to_hsl(255, 255, 255) == (180, 100, 100)


def test_hsl_to_rgb_part_17():
    assert hsl_to_rgb(240, 100, 0) == (0, 0, 0)
    assert hsl_to_rgb(240, 100, 10) == (0, 0, 51)
    assert hsl_to_rgb(240, 100, 20) == (0, 0, 102)
    assert hsl_to_rgb(240, 100, 30) == (0, 0, 153)
    assert hsl_to_rgb(240, 100, 40) == (0, 0, 204)
    assert hsl_to_rgb(240, 100, 50) == (0, 0, 255)
    assert hsl_to_rgb(240, 100, 60) == (51, 51, 255)
    assert hsl_to_rgb(240, 100, 70) == (102, 102, 255)
    assert hsl_to_rgb(240, 100, 80) == (153, 153, 255)
    assert hsl_to_rgb(240, 100, 90) == (204, 204, 255)
    assert hsl_to_rgb(240, 100, 100) == (255, 255, 255)


def test_rgb_to_hsl_part_17():
    # assert rgb_to_hsl(0, 0, 0) == (240, 100, 0)
    assert rgb_to_hsl(0, 0, 51) == (240, 100, 10)
    assert rgb_to_hsl(0, 0, 102) == (240, 100, 20)
    assert rgb_to_hsl(0, 0, 153) == (240, 100, 30)
    assert rgb_to_hsl(0, 0, 204) == (240, 100, 40)
    assert rgb_to_hsl(0, 0, 255) == (240, 100, 50)
    assert rgb_to_hsl(51, 51, 255) == (240, 100, 60)
    assert rgb_to_hsl(102, 102, 255) == (240, 100, 70)
    assert rgb_to_hsl(153, 153, 255) == (240, 100, 80)
    assert rgb_to_hsl(204, 204, 255) == (240, 100, 90)
    # assert rgb_to_hsl(255, 255, 255) == (240, 100, 100)


def test_hsl_to_rgb_part_18():
    assert hsl_to_rgb(300, 100, 0) == (0, 0, 0)
    assert hsl_to_rgb(300, 100, 10) == (51, 0, 51)
    assert hsl_to_rgb(300, 100, 20) == (102, 0, 102)
    assert hsl_to_rgb(300, 100, 30) == (153, 0, 153)
    assert hsl_to_rgb(300, 100, 40) == (204, 0, 204)
    assert hsl_to_rgb(300, 100, 50) == (255, 0, 255)
    assert hsl_to_rgb(300, 100, 60) == (255, 51, 255)
    assert hsl_to_rgb(300, 100, 70) == (255, 102, 255)
    assert hsl_to_rgb(300, 100, 80) == (255, 153, 255)
    assert hsl_to_rgb(300, 100, 90) == (255, 204, 255)
    assert hsl_to_rgb(300, 100, 100) == (255, 255, 255)


def test_rgb_to_hsl_part_18():
    # assert rgb_to_hsl(0, 0, 0) == (300, 100, 0)
    assert rgb_to_hsl(51, 0, 51) == (300, 100, 10)
    assert rgb_to_hsl(102, 0, 102) == (300, 100, 20)
    assert rgb_to_hsl(153, 0, 153) == (300, 100, 30)
    assert rgb_to_hsl(204, 0, 204) == (300, 100, 40)
    assert rgb_to_hsl(255, 0, 255) == (300, 100, 50)
    assert rgb_to_hsl(255, 51, 255) == (300, 100, 60)
    assert rgb_to_hsl(255, 102, 255) == (300, 100, 70)
    assert rgb_to_hsl(255, 153, 255) == (300, 100, 80)
    assert rgb_to_hsl(255, 204, 255) == (300, 100, 90)
    # assert rgb_to_hsl(255, 255, 255) == (300, 100, 100)
