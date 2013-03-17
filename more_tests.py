"""Additional tests from student contributors."""

import ants
import os
import sys
import imp
import unittest
from tests import AntTest, TestProblem9
from ucb import main

class AdditionalTests(AntTest):

    def setUp(self):
        imp.reload(ants)
        AntTest.setUp(self)
        self.queen = ants.QueenAnt()

    # A4

    def test_water_deadliness_2(self):
        error_msg = 'Water does not kill non-watersafe Insects'
        test_ants = [ants.Bee(1000000), ants.HarvesterAnt(), ants.Ant(), ants.ThrowerAnt()]
        test_ants[0].watersafe = False #Make the bee non-watersafe
        test_water = ants.Water('water_TestProblemA4_0')
        for test_ant in test_ants:
            test_water.add_insect(test_ant)
            self.assertIsNot(test_ant, test_water.ant, msg=error_msg)
            self.assertIs(0, test_ant.armor, msg=error_msg)

    def test_inheritance(self):
        """This test assumes that you have passed test_water_safety.
        This test may or may not cause... unusual behavior in other tests.
        Comment it out if you're worried.
        """
        error_msg = "Water does not inherit Place behavior"
        place_ai_method = ants.Place.add_insect #Save Place.add_insect method
        #Replace with fake method
        def fake_ai_method(self, insect):
            insect.reduce_armor(2)
        ants.Place.add_insect = fake_ai_method
        #Test putting bee in water
        test_bee = ants.Bee(10)
        test_water = ants.Water('water_TestProblemA4_0')
        test_water.add_insect(test_bee)
        #Should activate fake method, reduce armor
        self.assertIs(8, test_bee.armor, error_msg)
        #Restore method
        ants.Place.add_insect = place_ai_method

    #A5

    def test_fire_mod_damage(self):
        error_msg = 'FireAnt damage should not be static'
        place = self.colony.places['tunnel_0_0']
        bee = ants.Bee(900)
        place.add_insect(bee)
        #Amp up damage
        buffAnt = ants.FireAnt()
        buffAnt.damage = 500
        place.add_insect(buffAnt)

        bee.action(self.colony)
        self.assertEqual(400, bee.armor, error_msg)

    #B4

    def test_melee(self):
        error_msg = "ThrowerAnt doesn't attack bees on its own square."
        ant = ants.ThrowerAnt()
        self.colony.places['tunnel_0_0'].add_insect(ant)
        near_bee = ants.Bee(2)
        self.colony.places['tunnel_0_0'].add_insect(near_bee)

        self.assertIs(ant.nearest_bee(self.colony.hive), near_bee, error_msg)
        ant.action(self.colony)
        self.assertIs(1, near_bee.armor, error_msg)

    def test_random_shot(self):
        """This test is probabilistic. Even with a correct implementation,
        it will fail about 0.42% of the time.
        """
        error_msg = 'ThrowerAnt does not appear to choose random targets'
        #Place ant
        ant = ants.ThrowerAnt()
        self.colony.places['tunnel_0_0'].add_insect(ant)
        #Place two ultra-bees to test randomness
        bee = ants.Bee(1001)
        self.colony.places['tunnel_0_3'].add_insect(bee)
        self.colony.places['tunnel_0_3'].add_insect(ants.Bee(1001))

        #Throw 1000 times. bee should take ~1000*1/2 = ~500 damage,
        #and have ~501 remaining.
        for _ in range(1000):
            ant.action(self.colony)
        #Test if damage to bee 1 is within 3 SD (~46 damage)
        def dmg_within_tolerance():
            return abs(bee.armor-501) < 46
        self.assertIs(True, dmg_within_tolerance(), error_msg)

    # B5

    def test_range(self):
        error_msg = 'Range should not be static'
        #Buff ant range
        ant = ants.ShortThrower()
        ant.max_range = 10
        self.colony.places['tunnel_0_0'].add_insect(ant)

        #Place a bee out of normal range
        bee = ants.Bee(2)
        self.colony.places['tunnel_0_6'].add_insect(bee)
        ant.action(self.colony)

        self.assertIs(bee.armor, 1, error_msg)

    # A7

    def test_mod_damage(self):
        error_msg = 'Ninja damage should not be static'
        place = self.colony.places['tunnel_0_0']
        bee = ants.Bee(900)
        place.add_insect(bee)
        #Amp up damage
        buffNinja = ants.NinjaAnt()
        buffNinja.damage = 500
        place.add_insect(buffNinja)

        buffNinja.action(self.colony)
        self.assertEqual(400, bee.armor, error_msg)

    # B6

    def test_scuba_in_water(self):
        #Create water
        water = ants.Water('water')
        #Link water up to a tunnel
        water.entrance = self.colony.places['tunnel_0_1']
        target = self.colony.places['tunnel_0_4']
        #Set up ant/bee
        ant = ants.ScubaThrower()
        bee = ants.Bee(3)
        water.add_insect(ant)
        target.add_insect(bee)

        ant.action(self.colony)
        self.assertIs(2, bee.armor, "ScubaThrower doesn't throw in water")

    # B7

    def test_hungry_waits(self):
        """If you get an IndexError (not an AssertionError) when running
        this test, it's possible that your HungryAnt is trying to eat a
        bee when no bee is available.
        """

        #Add hungry ant
        hungry = ants.HungryAnt()
        place = self.colony.places['tunnel_0_0']
        place.add_insect(hungry)

        #Wait a few turns before adding bee
        for _ in range(5):
            hungry.action(self.colony)
        #Add bee
        bee = ants.Bee(3)
        place.add_insect(bee)
        hungry.action(self.colony)

        self.assertIs(0, bee.armor, 'HungryAnt didn\'t eat')

    def test_hungry_delay(self):
        #Add very hungry cater- um, ant
        very_hungry = ants.HungryAnt()
        very_hungry.time_to_digest = 0
        place = self.colony.places['tunnel_0_0']
        place.add_insect(very_hungry)

        #Add many bees
        for _ in range(100):
            place.add_insect(ants.Bee(3))
        #Eat many bees
        for _ in range(100):
            very_hungry.action(self.colony)

        self.assertIs(0, len(place.bees), 'Digestion time should not be static')

    # 8 (generously provided by an outside contributor)

    def test_remove_bodyguard(self):
        """This tests the following statement:
        "If a BodyguardAnt containing another ant is removed, then the
        ant it is containing should be placed where the BodyguardAnt
        used to be."
        Since this is optional, you can get a full score even if your
        program fails this doctest."""
        error_msg = 'Removing BodyguardAnt also removes containing ant'
        place = self.colony.places['tunnel_0_0']
        bodyguard = ants.BodyguardAnt()
        test_ant = ants.Ant(1)
        place.add_insect(bodyguard)
        place.add_insect(test_ant)
        self.colony.remove_ant('tunnel_0_0')
        self.assertIs(place.ant, test_ant, error_msg)

    def test_bodyguarded_ant_do_action(self):
        error_msg = "Bodyguarded ant does not perform its action"
        class TestAnt(ants.Ant):
            def action(self, colony):
                self.armor += 9000
        test_ant = TestAnt(1)
        place = self.colony.places['tunnel_0_0']
        bodyguard = ants.BodyguardAnt()
        place.add_insect(test_ant)
        place.add_insect(bodyguard)
        place.ant.action(self.colony)
        self.assertEqual(place.ant.ant.armor, 9001, error_msg)

    # 8

    def test_modified_container(self):
        #Test to see if we can construct a fake container
        error_msg = 'Container status should not be hard-coded'
        ant = ants.ThrowerAnt()
        ant.container = True
        ant.ant = None
        self.assertTrue(ant.can_contain(ants.ThrowerAnt()), error_msg)

    def test_modified_guard(self):
        #Test to see if we can contain a non-container bodyguard
        error_msg = 'Containable status should not be hard-coded'
        bodyguard = ants.BodyguardAnt()
        mod_guard = ants.BodyguardAnt()
        mod_guard.container = False
        self.assertTrue(bodyguard.can_contain(mod_guard), error_msg)

    # 9 (outside contributor)

    def test_removing_bodyguarded_queen(self):
        error_msg = 'Bodyguarded queen can be removed!'
        queen = self.queen
        guard = ants.BodyguardAnt()
        place = self.colony.places['tunnel_0_0']
        place.add_insect(queen)
        place.add_insect(guard)
        self.colony.remove_ant('tunnel_0_0')
        self.assertIs(place.ant, queen, error_msg)
        if place.ant.container:
            # Bodyguard ant should still contain queen, if it isn't removed
            self.assertFalse(place.ant.ant, queen, error_msg)

    # 9

    def test_double_continuous(self):
        """This test makes the queen buff one ant, then the other, to see
        if the queen will continually buff newly added ants.
        """
        self.colony.places['tunnel_0_0'].add_insect(ants.ThrowerAnt())
        self.colony.places['tunnel_0_2'].add_insect(self.queen)
        self.queen.action(self.colony)

        #Add ant and buff
        ant = ants.ThrowerAnt()
        self.colony.places['tunnel_0_1'].add_insect(ant)
        self.queen.action(self.colony)

        #Attack a bee
        bee = ants.Bee(3)
        self.colony.places['tunnel_0_4'].add_insect(bee)
        ant.action(self.colony)
        self.assertEqual(1, bee.armor, "Queen does not buff new ants")


@main
def main(*args):
    import argparse
    parser = argparse.ArgumentParser(description="Run Ants Tests")
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()
    stdout = sys.stdout
    with open(os.devnull, 'w') as sys.stdout:
        verbosity = 2 if args.verbose else 1
        tests = unittest.main(exit=False, verbosity=verbosity)
    sys.stdout = stdout
