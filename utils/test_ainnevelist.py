"""
AinneveList test suite.
"""
from django.test import TestCase
from .ainnevelist import AinneveList


class AinneveListTestCase(TestCase):
    """Test AinneveList functionality."""
    def setUp(self):
        self.simple_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                            'Friday', 'Saturday', 'Sunday']
        self.simple_dict = {'Strength': 6, 'Perception': 5, 'Intelligence': 4,
                            'Dexterity': 3, 'Charisma': 2, 'Vitality': 1,
                            'Magic': 0}
        self.structured_dict = [
            {'lbl':'Carry Weight', 'val': '50|n / |w180',
             'lsep': '=>', 'vwidth': 10, 'sort': 3},
            {'lbl': 'Encumbrance', 'val': '+2', 'vwidth': 3, 'sort': 2},
            {'lbl': 'Movement', 'val': 5, 'lcolor': '|b',
             'vcolor': '|y', 'sort': 1},
        ]

    def test_input_list(self):
        """test simple list input data format in default three-column layout"""
        lst = AinneveList(self.simple_list, columns=3)
        output = """\
+-------------------------+-------------------------+-------------------------+
|| Monday                  || Tuesday                 || Wednesday               ||
|| Thursday                || Friday                  || Saturday                ||
|| Sunday                  ||                         ||                         ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)

    def test_input_dict(self):
        """test simple dict input data format"""
        lst = AinneveList(self.simple_dict, columns=3)
        output = """\
+-------------------------+-------------------------+-------------------------+
|| Dexterity         :   3 || Perception        :   5 || Magic             :   0 ||
|| Intelligence      :   4 || Vitality          :   1 || Charisma          :   2 ||
|| Strength          :   6 ||                         ||                         ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)

    def test_input_struct_dict(self):
        """test structured dict input data format"""
        lst = AinneveList(self.structured_dict, columns=3)
        output = """\
+-------------------------+-------------------------+-------------------------+
|| Carry W.. =>   50|n / |w180 || Encumbrance       :  +2 || |bMovement         |n : |y  5|n ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)

    def test_onecol_layout(self):
        """test default one-column layout"""
        lst = AinneveList(self.simple_list, columns=1)
        output = """\
+-----------------------------------------------------------------------------+
|| Monday                                                                      ||
|| Tuesday                                                                     ||
|| Wednesday                                                                   ||
|| Thursday                                                                    ||
|| Friday                                                                      ||
|| Saturday                                                                    ||
|| Sunday                                                                      ||
+-----------------------------------------------------------------------------+"""
        self.assertEqual(str(lst), output)

    def test_twocol_layout(self):
        """test default two-column layout"""
        lst = AinneveList(self.simple_list, columns=2)
        output = """\
+--------------------------------------+--------------------------------------+
|| Monday                               || Tuesday                              ||
|| Wednesday                            || Thursday                             ||
|| Friday                               || Saturday                             ||
|| Sunday                               ||                                      ||
+--------------------------------------+--------------------------------------+"""
        self.assertEqual(str(lst), output)

    def test_offset_layout(self):
        """test complex layout using the `layout` argument"""
        lst = AinneveList(self.simple_list,
                          layout=['column-3', 'offset-1', 'column-2'])
        output = """\
+--------------------------------------+            +-------------------------+
|| Monday                               ||            || Tuesday                 ||
|| Wednesday                            ||            || Thursday                ||
|| Friday                               ||            || Saturday                ||
|| Sunday                               ||            ||                         ||
+--------------------------------------+            +-------------------------+"""
        self.assertEqual(str(lst), output)

    def test_vertical_fill(self):
        """test fill_dir='v' functionality"""
        lst = AinneveList(self.simple_list, columns=3, fill_dir='v')
        output = """\
+-------------------------+-------------------------+-------------------------+
|| Monday                  || Thursday                || Sunday                  ||
|| Tuesday                 || Friday                  ||                         ||
|| Wednesday               || Saturday                ||                         ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)

    def test_orderby(self):
        """test sorting functionality"""
        # 'val' key on simple list
        lst = AinneveList(self.simple_list, columns=1, orderby='val')
        output = """\
+-----------------------------------------------------------------------------+
|| Friday                                                                      ||
|| Monday                                                                      ||
|| Saturday                                                                    ||
|| Sunday                                                                      ||
|| Thursday                                                                    ||
|| Tuesday                                                                     ||
|| Wednesday                                                                   ||
+-----------------------------------------------------------------------------+"""
        self.assertEqual(str(lst), output)
        # 'lbl' key on simple dict
        lst = AinneveList(self.simple_dict, columns=1, orderby='lbl')
        output = """\
+-----------------------------------------------------------------------------+
|| Charisma                                                              :   2 ||
|| Dexterity                                                             :   3 ||
|| Intelligence                                                          :   4 ||
|| Magic                                                                 :   0 ||
|| Perception                                                            :   5 ||
|| Strength                                                              :   6 ||
|| Vitality                                                              :   1 ||
+-----------------------------------------------------------------------------+"""
        self.assertEqual(str(lst), output)
        # 'val' key on simple dict
        lst = AinneveList(self.simple_dict, columns=1, orderby='val')
        output = """\
+-----------------------------------------------------------------------------+
|| Magic                                                                 :   0 ||
|| Vitality                                                              :   1 ||
|| Charisma                                                              :   2 ||
|| Dexterity                                                             :   3 ||
|| Intelligence                                                          :   4 ||
|| Perception                                                            :   5 ||
|| Strength                                                              :   6 ||
+-----------------------------------------------------------------------------+"""
        self.assertEqual(str(lst), output)
        # 'sort' key on structured dict
        lst = AinneveList(self.structured_dict, columns=1, orderby='sort')
        output = """\
+-----------------------------------------------------------------------------+
|| |bMovement                                                             |n : |y  5|n ||
|| Encumbrance                                                           :  +2 ||
|| Carry Weight                                                  =>   50|n / |w180 ||
+-----------------------------------------------------------------------------+"""
        self.assertEqual(str(lst), output)

    def test_width(self):
        """test varying widths for AinneveForm"""
        # narrower than standard
        lst = AinneveList(self.simple_list, columns=3, width=57)
        output = """\
+------------------+-----------------+------------------+
|| Monday           || Tuesday         || Wednesday        ||
|| Thursday         || Friday          || Saturday         ||
|| Sunday           ||                 ||                  ||
+------------------+-----------------+------------------+"""
        self.assertEqual(str(lst), output)
        # wider than standard
        lst = AinneveList(self.simple_list, columns=3, width=92)
        output = """\
+-----------------------------+------------------------------+-----------------------------+
|| Monday                      || Tuesday                      || Wednesday                   ||
|| Thursday                    || Friday                       || Saturday                    ||
|| Sunday                      ||                              ||                             ||
+-----------------------------+------------------------------+-----------------------------+"""
        self.assertEqual(str(lst), output)
        # too narrow; doesn't break down well, but at least it's symmetrical
        lst = AinneveList(self.simple_list, columns=3, width=6)
        output = "+-++-+\n||  ||  ||  ||\n||  ||  ||  ||\n||  ||  ||  ||\n+-++-+"
        self.assertEqual(str(lst), output)

    def test_lsep(self):
        """test alternate label separator and separator override"""
        lst = AinneveList(self.structured_dict, columns=1, width=50, lsep='[-')
        output = """\
+------------------------------------------------+
|| Carry Weight                     =>   50|n / |w180 ||
|| Encumbrance                             [-  +2 ||
|| |bMovement                               |n [- |y  5|n ||
+------------------------------------------------+"""
        self.assertEqual(str(lst), output)

    def test_colors(self):
        """test color arguments and overrides"""
        lst = AinneveList(self.structured_dict, columns=1, width=50,
                          lcolor='|r', vcolor='|w')
        output = """\
+------------------------------------------------+
|| |rCarry Weight                    |n => |w  50|n / |w180|n ||
|| |rEncumbrance                             |n : |w +2|n ||
|| |bMovement                                |n : |y  5|n ||
+------------------------------------------------+"""
        self.assertEqual(str(lst), output)
        lst = AinneveList(self.simple_list, columns=3,
                          lcolor='|X',  # should not appear in output
                          vcolor='|r')
        output = """\
+-------------------------+-------------------------+-------------------------+
|| |rMonday                 |n || |rTuesday                |n || |rWednesday              |n ||
|| |rThursday               |n || |rFriday                 |n || |rSaturday               |n ||
|| |rSunday                 |n || |r                       |n || |r                       |n ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)

    def test_padding(self):
        """test modifying list padding"""
        # wide
        lst = AinneveList(self.simple_list, columns=1, width=50,
                          padding=10)
        output = """\
+------------------------------------------------+
||          Monday                                ||
||          Tuesday                               ||
||          Wednesday                             ||
||          Thursday                              ||
||          Friday                                ||
||          Saturday                              ||
||          Sunday                                ||
+------------------------------------------------+"""
        self.assertEqual(str(lst), output)
        # no padding
        lst = AinneveList(self.simple_list, columns=1, width=50,
                          padding=0)
        output = """\
+------------------------------------------------+
||Monday                                          ||
||Tuesday                                         ||
||Wednesday                                       ||
||Thursday                                        ||
||Friday                                          ||
||Saturday                                        ||
||Sunday                                          ||
+------------------------------------------------+"""
        self.assertEqual(str(lst), output)

    def test_has_border(self):
        """test disabling borders"""
        lst = AinneveList(self.simple_list, columns=3, width=50,
                          has_border=False)
        output = (' Monday           Tuesday         Wednesday       \n'
                  ' Thursday         Friday          Saturday        \n'
                  ' Sunday                                           ')
        self.assertEqual(str(lst), output)

    def test_lalign(self):
        """test label alignment property"""
        lst = AinneveList(self.simple_dict, columns=3, lalign='r')
        output = """\
+-------------------------+-------------------------+-------------------------+
||         Dexterity :   3 ||        Perception :   5 ||             Magic :   0 ||
||      Intelligence :   4 ||          Vitality :   1 ||          Charisma :   2 ||
||          Strength :   6 ||                         ||                         ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)
        lst.lalign = '^'
        output = """\
+-------------------------+-------------------------+-------------------------+
||     Dexterity     :   3 ||    Perception     :   5 ||       Magic       :   0 ||
||   Intelligence    :   4 ||     Vitality      :   1 ||     Charisma      :   2 ||
||     Strength      :   6 ||                         ||                         ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)

    def test_valign(self):
        """test value alignment property"""
        lst = AinneveList(self.simple_dict, columns=3, valign='l')
        output = """\
+-------------------------+-------------------------+-------------------------+
|| Dexterity         : 3   || Perception        : 5   || Magic             : 0   ||
|| Intelligence      : 4   || Vitality          : 1   || Charisma          : 2   ||
|| Strength          : 6   ||                         ||                         ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)
        lst.valign = '^'
        output = """\
+-------------------------+-------------------------+-------------------------+
|| Dexterity         :  3  || Perception        :  5  || Magic             :  0  ||
|| Intelligence      :  4  || Vitality          :  1  || Charisma          :  2  ||
|| Strength          :  6  ||                         ||                         ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)

    def test_no_line_breaks(self):
        """test linebreak removal"""
        lst = AinneveList(['one line', 'two\nlines',
                           'windows style\r\nsomehow'],
                          columns=3)
        output = """\
+-------------------------+-------------------------+-------------------------+
|| one line                || two lines               || windows style somehow   ||
+-------------------------+-------------------------+-------------------------+"""
        self.assertEqual(str(lst), output)
