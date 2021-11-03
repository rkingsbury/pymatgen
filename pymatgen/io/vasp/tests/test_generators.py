# coding: utf-8
# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

import os

import pytest  # type: ignore
from monty.json import MontyDecoder
from _pytest.monkeypatch import MonkeyPatch  # type: ignore

from pymatgen.core import SETTINGS
from pymatgen.core import Lattice, Species, Structure
from pymatgen.io.vasp.inputs import Poscar
from pymatgen.io.vasp.sets import *
from pymatgen.io.vasp.generators import *
from pymatgen.util.testing import PymatgenTest

# MODULE_DIR = Path(__file__).resolve().parent

# dec = MontyDecoder()


# class MITMPRelaxGenTest(PymatgenTest):
#     @classmethod
#     def setUpClass(cls):
#         cls.monkeypatch = MonkeyPatch()

#         filepath = cls.TEST_FILES_DIR / "POSCAR"
#         poscar = Poscar.from_file(filepath)
#         cls.structure = poscar.structure
#         cls.coords = [[0, 0, 0], [0.75, 0.5, 0.75]]
#         cls.lattice = Lattice(
#             [
#                 [3.8401979337, 0.00, 0.00],
#                 [1.9200989668, 3.3257101909, 0.00],
#                 [0.00, -2.2171384943, 3.1355090603],
#             ]
#         )

#         cls.mitset = MITRelaxGen().get_input_set(cls.structure)
#         cls.mitset_unsorted = MITRelaxGen(sort_structure=False).get_input_set(
#             cls.structure,
#         )
#         cls.mpset = MPRelaxGen().get_input_set(cls.structure)

#     def setUp(self):
#         warnings.simplefilter("ignore")

#     def tearDown(self):
#         warnings.simplefilter("default")

#     def test_set_gen_equivalence(self):
#         """
#         Verify that the InputSet generated by MPRelaxSet() and MPRelaxGen() are identical
#         (except for the class name)
#         """
#         d_set = MPRelaxSet(self.structure).as_dict()
#         del d_set["@class"]

#         d_gen = self.mpset.as_dict()
#         del d_set["@class"]

#         assert d_set == d_gen

#     def test_metal_check(self):
#         structure = Structure.from_spacegroup("Fm-3m", Lattice.cubic(3), ["Cu"], [[0, 0, 0]])

#         with warnings.catch_warnings(record=True) as w:
#             # Cause all warnings to always be triggered.
#             warnings.simplefilter("always")
#             # Trigger a warning.
#             vis = MITRelaxGen().get_input_set(structure)
#             incar = vis.incar
#             # Verify some things
#             self.assertIn("ISMEAR", str(w[-1].message))

#     def test_poscar(self):
#         structure = Structure(self.lattice, ["Fe", "Mn"], self.coords)
#         mitparamset = MITRelaxGen(sort_structure=False).get_input_set(structure)
#         s_unsorted = mitparamset.poscar.structure
#         mitparamset = MITRelaxGen(sort_structure=True).get_input_set(structure)
#         s_sorted = mitparamset.poscar.structure
#         self.assertEqual(s_unsorted[0].specie.symbol, "Fe")
#         self.assertEqual(s_sorted[0].specie.symbol, "Mn")

#     def test_potcar_symbols(self):
#         coords = []
#         coords.append([0, 0, 0])
#         coords.append([0.75, 0.5, 0.75])
#         coords.append([0.75, 0.25, 0.75])
#         lattice = Lattice(
#             [
#                 [3.8401979337, 0.00, 0.00],
#                 [1.9200989668, 3.3257101909, 0.00],
#                 [0.00, -2.2171384943, 3.1355090603],
#             ]
#         )
#         structure = Structure(lattice, ["P", "Fe", "O"], coords)
#         mitparamset = MITRelaxGen().get_input_set(structure)
#         syms = mitparamset.potcar_symbols
#         self.assertEqual(syms, ["Fe", "P", "O"])
#         paramset = MPRelaxGen(sort_structure=False).get_input_set(structure)
#         syms = paramset.potcar_symbols
#         self.assertEqual(syms, ["P", "Fe_pv", "O"])

#     def test_potcar_validation(self):
#         structure = Structure(self.lattice, ["P", "Fe"], self.coords)
#         # Use pytest's monkeypatch to temporarily point pymatgen to a directory
#         # containing the wrong POTCARs (LDA potcars in a PBE directory)
#         with self.monkeypatch.context() as m:
#             m.setitem(SETTINGS, "PMG_VASP_PSP_DIR", str(self.TEST_FILES_DIR / "wrong_potcars"))
#             with pytest.warns(BadInputSetWarning, match="not known by pymatgen"):
#                 MITRelaxGen().get_input_set(structure).potcar

#     def test_lda_potcar(self):
#         structure = Structure(self.lattice, ["P", "Fe"], self.coords)
#         p = (
#             MITRelaxGen(user_potcar_functional="LDA")
#             .get_input_set(
#                 structure,
#             )
#             .potcar
#         )
#         self.assertEqual(p.functional, "LDA")

#     def test_nelect(self):
#         coords = [[0] * 3, [0.5] * 3, [0.75] * 3]
#         lattice = Lattice.cubic(4)
#         s = Structure(lattice, ["Si", "Si", "Fe"], coords)
#         self.assertAlmostEqual(MITRelaxGen().get_input_set(s).nelect, 16)

#         # Test estimate of number of bands (function of nelect) with nmag>0
#         self.assertAlmostEqual(MITRelaxGen().get_input_set(s).estimate_nbands(), 13)
#         self.assertAlmostEqual(MPRelaxGen().get_input_set(s).estimate_nbands(), 17)

#         # Test estimate of number of bands (function of nelect) with nmag==0
#         s = Structure(lattice, ["Si", "Si", "Si"], coords)
#         self.assertAlmostEqual(MITRelaxGen().get_input_set(s).estimate_nbands(), 11)
#         self.assertAlmostEqual(MITRelaxGen().get_input_set(s).estimate_nbands(), 11)

#         # Check that it works even when oxidation states are present. Was a bug
#         # previously.
#         s = Structure(lattice, ["Si4+", "Si4+", "Fe2+"], coords)
#         self.assertAlmostEqual(MITRelaxGen().get_input_set(s).nelect, 16)
#         self.assertAlmostEqual(MPRelaxGen().get_input_set(s).nelect, 22)

#         # Check that it works for disordered structure. Was a bug previously
#         s = Structure(lattice, ["Si4+", "Fe2+", "Si4+"], coords)
#         self.assertAlmostEqual(MITRelaxGen().get_input_set(s).nelect, 16)
#         self.assertAlmostEqual(MPRelaxGen().get_input_set(s).nelect, 22)

#     def test_get_incar(self):

#         incar = self.mpset.incar

#         self.assertEqual(incar["LDAUU"], [5.3, 0, 0])
#         self.assertAlmostEqual(incar["EDIFF"], 0.0012)

#         incar = self.mitset.incar
#         self.assertEqual(incar["LDAUU"], [4.0, 0, 0])
#         self.assertAlmostEqual(incar["EDIFF"], 1e-5)

#         si = 14
#         coords = []
#         coords.append(np.array([0, 0, 0]))
#         coords.append(np.array([0.75, 0.5, 0.75]))

#         # Silicon structure for testing.
#         latt = Lattice(
#             np.array(
#                 [
#                     [3.8401979337, 0.00, 0.00],
#                     [1.9200989668, 3.3257101909, 0.00],
#                     [0.00, -2.2171384943, 3.1355090603],
#                 ]
#             )
#         )
#         struct = Structure(latt, [si, si], coords)
#         incar = MPRelaxGen().get_input_set(struct).incar
#         self.assertNotIn("LDAU", incar)

#         coords = []
#         coords.append([0, 0, 0])
#         coords.append([0.75, 0.5, 0.75])
#         lattice = Lattice(
#             [
#                 [3.8401979337, 0.00, 0.00],
#                 [1.9200989668, 3.3257101909, 0.00],
#                 [0.00, -2.2171384943, 3.1355090603],
#             ]
#         )
#         struct = Structure(lattice, ["Fe", "Mn"], coords)

#         incar = MPRelaxGen().get_input_set(struct).incar
#         self.assertNotIn("LDAU", incar)

#         # check fluorides
#         struct = Structure(lattice, ["Fe", "F"], coords)
#         incar = MPRelaxGen().get_input_set(struct).incar
#         self.assertEqual(incar["LDAUU"], [5.3, 0])
#         self.assertEqual(incar["MAGMOM"], [5, 0.6])

#         struct = Structure(lattice, ["Fe", "F"], coords)
#         incar = MITRelaxGen().get_input_set(struct).incar
#         self.assertEqual(incar["LDAUU"], [4.0, 0])

#         # Make sure this works with species.
#         struct = Structure(lattice, ["Fe2+", "O2-"], coords)
#         incar = MPRelaxGen().get_input_set(struct).incar
#         self.assertEqual(incar["LDAUU"], [5.3, 0])

#         struct = Structure(lattice, ["Fe", "Mn"], coords, site_properties={"magmom": (5.2, -4.5)})
#         incar = MPRelaxGen().get_input_set(struct).incar
#         self.assertEqual(incar["MAGMOM"], [-4.5, 5.2])

#         incar = MITRelaxGen(sort_structure=False).get_input_set(struct).incar
#         self.assertEqual(incar["MAGMOM"], [5.2, -4.5])

#         struct = Structure(lattice, [Species("Fe", 2, {"spin": 4.1}), "Mn"], coords)
#         incar = MPRelaxGen().get_input_set(struct).incar
#         self.assertEqual(incar["MAGMOM"], [5, 4.1])

#         struct = Structure(lattice, ["Mn3+", "Mn4+"], coords)
#         incar = MITRelaxGen().get_input_set(struct).incar
#         self.assertEqual(incar["MAGMOM"], [4, 3])

#         userset = MPRelaxGen(user_incar_settings={"MAGMOM": {"Fe": 10, "S": -5, "Mn3+": 100}}).get_input_set(struct)
#         self.assertEqual(userset.incar["MAGMOM"], [100, 0.6])

#         noencutset = MPRelaxGen(user_incar_settings={"ENCUT": None}).get_input_set(struct)
#         self.assertNotIn("ENCUT", noencutset.incar)

#         # sulfide vs sulfate test

#         coords = []
#         coords.append([0, 0, 0])
#         coords.append([0.75, 0.5, 0.75])
#         coords.append([0.25, 0.5, 0])

#         struct = Structure(lattice, ["Fe", "Fe", "S"], coords)
#         incar = MITRelaxGen().get_input_set(struct).incar
#         self.assertEqual(incar["LDAUU"], [1.9, 0])

#         # Make sure Matproject sulfides are ok.
#         self.assertNotIn("LDAUU", MPRelaxGen().get_input_set(struct).incar)

#         struct = Structure(lattice, ["Fe", "S", "O"], coords)
#         incar = MITRelaxGen().get_input_set(struct).incar
#         self.assertEqual(incar["LDAUU"], [4.0, 0, 0])

#         # Make sure Matproject sulfates are ok.
#         self.assertEqual(MPRelaxGen().get_input_set(struct).incar["LDAUU"], [5.3, 0, 0])

#         # test for default LDAUU value
#         userset_ldauu_fallback = MPRelaxGen(user_incar_settings={"LDAUU": {"Fe": 5.0, "S": 0}}).get_input_set(struct)
#         self.assertEqual(userset_ldauu_fallback.incar["LDAUU"], [5.0, 0, 0])

#         # Expected to be oxide (O is the most electronegative atom)
#         s = Structure(lattice, ["Fe", "O", "S"], coords)
#         incar = MITRelaxGen().get_input_set(s).incar
#         self.assertEqual(incar["LDAUU"], [4.0, 0, 0])

#         # Expected to be chloride (Cl is the most electronegative atom)
#         s = Structure(lattice, ["Fe", "Cl", "S"], coords)
#         incar = MITRelaxGen(user_incar_settings={"LDAU": True}).get_input_set(s).incar
#         self.assertFalse("LDAUU" in incar)  # LDAU = False

#         # User set a compound to be sulfide by specifing values of "LDAUL" etc.
#         s = Structure(lattice, ["Fe", "Cl", "S"], coords)
#         incar = (
#             MITRelaxGen(
#                 user_incar_settings={
#                     "LDAU": True,
#                     "LDAUL": {"Fe": 3},
#                     "LDAUU": {"Fe": 1.8},
#                 },
#             )
#             .get_input_set(s)
#             .incar
#         )
#         self.assertEqual(incar["LDAUL"], [3.0, 0, 0])
#         self.assertEqual(incar["LDAUU"], [1.8, 0, 0])

#         # test that van-der-Waals parameters are parsed correctly
#         incar = MITRelaxGen(vdw="optB86b").get_input_set(struct).incar
#         self.assertEqual(incar["GGA"], "Mk")
#         self.assertEqual(incar["LUSE_VDW"], True)
#         self.assertEqual(incar["PARAM1"], 0.1234)

#         # Test that NELECT is updated when a charge is present
#         si = 14
#         coords = []
#         coords.append(np.array([0, 0, 0]))
#         coords.append(np.array([0.75, 0.5, 0.75]))

#         # Silicon structure for testing.
#         latt = Lattice(
#             np.array(
#                 [
#                     [3.8401979337, 0.00, 0.00],
#                     [1.9200989668, 3.3257101909, 0.00],
#                     [0.00, -2.2171384943, 3.1355090603],
#                 ]
#             )
#         )
#         struct = Structure(latt, [si, si], coords, charge=1)
#         mpr = MPRelaxGen(use_structure_charge=True).get_input_set(struct)
#         self.assertEqual(mpr.incar["NELECT"], 7, "NELECT not properly set for nonzero charge")

#         # test that NELECT does not get set when use_structure_charge = False
#         mpr = MPRelaxGen(use_structure_charge=False).get_input_set(struct)
#         self.assertFalse(
#             "NELECT" in mpr.incar.keys(),
#             "NELECT should not be set when " "use_structure_charge is False",
#         )

#         struct = Structure(latt, ["Co", "O"], coords)
#         mpr = MPRelaxGen().get_input_set(struct)
#         self.assertEqual(mpr.incar["MAGMOM"], [0.6, 0.6])
#         struct = Structure(latt, ["Co4+", "O"], coords)
#         mpr = MPRelaxGen().get_input_set(struct)
#         self.assertEqual(mpr.incar["MAGMOM"], [1, 0.6])

#         # test passing user_incar_settings and user_kpoint_settings of None
#         sets = [
#             MPRelaxGen(user_incar_settings=None, user_kpoints_settings=None).get_input_set(struct),
#             # MPStaticSet(struct, user_incar_settings=None, user_kpoints_settings=None),
#             # MPNonSCFSet(struct, user_incar_settings=None, user_kpoints_settings=None),
#         ]
#         for mp_set in sets:
#             self.assertNotEqual(mp_set.kpoints, None)
#             self.assertNotEqual(mp_set.incar, None)

#     def test_get_kpoints(self):
#         kpoints = MPRelaxGen().get_input_set(self.structure).kpoints
#         self.assertEqual(kpoints.kpts, [[2, 4, 5]])
#         self.assertEqual(kpoints.style, Kpoints.supported_modes.Gamma)

#         kpoints = MPRelaxGen(user_kpoints_settings={"reciprocal_density": 1000}).get_input_set(self.structure).kpoints
#         self.assertEqual(kpoints.kpts, [[6, 10, 13]])
#         self.assertEqual(kpoints.style, Kpoints.supported_modes.Gamma)

#         kpoints_obj = Kpoints(kpts=[[3, 3, 3]])
#         kpoints_return = MPRelaxGen(user_kpoints_settings=kpoints_obj).get_input_set(self.structure).kpoints
#         self.assertEqual(kpoints_return.kpts, [[3, 3, 3]])

#         kpoints = self.mitset.kpoints
#         self.assertEqual(kpoints.kpts, [[25]])
#         self.assertEqual(kpoints.style, Kpoints.supported_modes.Automatic)

#         recip_paramset = MPRelaxGen(force_gamma=True).get_input_set(self.structure)
#         recip_paramset.kpoints_settings = {"reciprocal_density": 40}
#         kpoints = recip_paramset.kpoints
#         self.assertEqual(kpoints.kpts, [[2, 4, 5]])
#         self.assertEqual(kpoints.style, Kpoints.supported_modes.Gamma)

#     def test_get_vasp_input(self):
#         d = self.mitset.get_vasp_input()
#         self.assertEqual(d["INCAR"]["ISMEAR"], -5)
#         s = self.structure.copy()
#         s.make_supercell(4)
#         paramset = MPRelaxGen().get_input_set(s)
#         d = paramset.get_vasp_input()
#         self.assertEqual(d["INCAR"]["ISMEAR"], 0)

#     # def test_MPMetalRelaxSet(self):
#     #     mpmetalset = MPMetalRelaxSet(self.get_structure("Sn"))
#     #     incar = mpmetalset.incar
#     #     self.assertEqual(incar["ISMEAR"], 1)
#     #     self.assertEqual(incar["SIGMA"], 0.2)
#     #     kpoints = mpmetalset.kpoints
#     #     self.assertArrayAlmostEqual(kpoints.kpts[0], [5, 5, 5])

#     def test_as_from_dict(self):
#         mitset = MITRelaxGen().get_input_set(self.structure)
#         mpset = MPRelaxGen().get_input_set(self.structure)
#         mpuserset = MPRelaxGen(
#             user_incar_settings={"MAGMOM": {"Fe": 10, "S": -5, "Mn3+": 100}},
#         ).get_input_set(self.structure)

#         d = mitset.as_dict()
#         v = dec.process_decoded(d)
#         self.assertEqual(v._config_dict["INCAR"]["LDAUU"]["O"]["Fe"], 4)

#         d = mpset.as_dict()
#         v = dec.process_decoded(d)
#         self.assertEqual(v._config_dict["INCAR"]["LDAUU"]["O"]["Fe"], 5.3)

#         d = mpuserset.as_dict()
#         v = dec.process_decoded(d)
#         # self.assertEqual(type(v), MPVaspInputSet)
#         self.assertEqual(v.user_incar_settings["MAGMOM"], {"Fe": 10, "S": -5, "Mn3+": 100})

#     def test_hubbard_off_and_ediff_override(self):
#         p = MPRelaxGen(user_incar_settings={"LDAU": False, "EDIFF": 1e-10}).get_input_set(self.structure)
#         self.assertNotIn("LDAUU", p.incar)
#         self.assertEqual(p.incar["EDIFF"], 1e-10)
#         # after testing, we have determined LMAXMIX should still be 4 for d-block
#         # even if U is turned off (thanks Andrew Rosen for reporting)
#         self.assertEqual(p.incar["LMAXMIX"], 4)

#     def test_write_input(self):
#         self.mitset.write_input(".", make_dir_if_not_present=True)
#         for f in ["INCAR", "KPOINTS", "POSCAR", "POTCAR"]:
#             self.assertTrue(os.path.exists(f))
#         self.assertFalse(os.path.exists("Fe4P4O16.cif"))

#         self.mitset.write_input(".", make_dir_if_not_present=True, include_cif=True)
#         self.assertTrue(os.path.exists("Fe4P4O16.cif"))
#         for f in ["INCAR", "KPOINTS", "POSCAR", "POTCAR", "Fe4P4O16.cif"]:
#             os.remove(f)

#         self.mitset.write_input(".", make_dir_if_not_present=True, potcar_spec=True)

#         for f in ["INCAR", "KPOINTS", "POSCAR"]:
#             self.assertTrue(os.path.exists(f))
#         self.assertFalse(os.path.exists("POTCAR"))
#         self.assertTrue(os.path.exists("POTCAR.spec"))
#         for f in ["INCAR", "KPOINTS", "POSCAR", "POTCAR.spec"]:
#             os.remove(f)

#     def test_user_potcar_settings(self):
#         vis = MPRelaxGen(user_potcar_settings={"Fe": "Fe"}).get_input_set(self.structure)
#         potcar = vis.potcar
#         self.assertEqual(potcar.symbols, ["Fe", "P", "O"])

#     def test_valid_magmom_struct(self):
#         # First test the helper function
#         struct = self.structure.copy()
#         get_valid_magmom_struct(structure=struct, inplace=True, spin_mode="v")
#         props = [isite.properties for isite in struct.sites]
#         self.assertEquals(props, [{"magmom": [1.0, 1.0, 1.0]}] * len(props))

#         struct = self.structure.copy()
#         get_valid_magmom_struct(structure=struct, inplace=True, spin_mode="s")
#         props = [isite.properties for isite in struct.sites]
#         self.assertEquals(props, [{"magmom": 1.0}] * len(props))
#         struct.insert(0, "Li", [0, 0, 0])
#         get_valid_magmom_struct(structure=struct, inplace=True, spin_mode="a")
#         props = [isite.properties for isite in struct.sites]
#         self.assertEquals(props, [{"magmom": 1.0}] * len(props))

#         struct = self.structure.copy()
#         get_valid_magmom_struct(structure=struct, inplace=True, spin_mode="v")
#         struct.insert(0, "Li", [0, 0, 0], properties={"magmom": 10.0})
#         with self.assertRaises(TypeError) as context:
#             get_valid_magmom_struct(structure=struct, inplace=True, spin_mode="a")
#         self.assertTrue("Magmom type conflict" in str(context.exception))

#         # Test the behavior of MPRelaxGen to automatically fill in the missing magmom
#         struct = self.structure.copy()
#         get_valid_magmom_struct(structure=struct, inplace=True, spin_mode="s")
#         struct.insert(0, "Li", [0, 0, 0])

#         vis = MPRelaxGen(user_potcar_settings={"Fe": "Fe"}, validate_magmom=False).get_input_set(struct)
#         with self.assertRaises(TypeError) as context:
#             print(vis.get_vasp_input())

#         self.assertTrue("argument must be a string" in str(context.exception))
#         vis = MPRelaxGen(user_potcar_settings={"Fe": "Fe"}, validate_magmom=True).get_input_set(struct)
#         self.assertEqual(vis.get_vasp_input()["INCAR"]["MAGMOM"], [1.0] * len(struct))


# class MPScanRelaxGenTest(PymatgenTest):
#     def setUp(self):
#         file_path = self.TEST_FILES_DIR / "POSCAR"
#         poscar = Poscar.from_file(file_path)
#         self.struct = poscar.structure
#         self.mp_scan_set = MPScanRelaxSet(
#             self.struct, user_potcar_functional="PBE_52", user_incar_settings={"NSW": 500}
#         )
#         warnings.simplefilter("ignore")
#         self.mp_scan_gen = MPScanRelaxGen(user_potcar_functional="PBE_52", user_incar_settings={"NSW": 500})

#     def tearDown(self):
#         warnings.simplefilter("default")

#     def test_set_gen_equivalence(self):
#         """
#         Verify that the InputSet generated by MPScanRelaxSet() and MPScanRelaxGen() are identical
#         (except for the bandgap attribute and class name)
#         """
#         d_set = self.mp_scan_set.as_dict()
#         del d_set["@class"]
#         del d_set["bandgap"]

#         d_gen = self.mp_scan_gen().get_input_set(self.struct).as_dict()
#         del d_set["@class"]

#         assert d_set == d_gen

#     def test_incar(self):
#         incar = self.mp_scan_gen.get_input_set(self.struct).incar
#         self.assertEqual(incar["METAGGA"], "R2scan")
#         self.assertEqual(incar["LASPH"], True)
#         self.assertEqual(incar["ENAUG"], 1360)
#         self.assertEqual(incar["ENCUT"], 680)
#         self.assertEqual(incar["NSW"], 500)
#         # the default POTCAR contains metals
#         self.assertEqual(incar["KSPACING"], 0.22)
#         self.assertEqual(incar["ISMEAR"], 2)
#         self.assertEqual(incar["SIGMA"], 0.2)

#     def test_scan_substitute(self):
#         mp_scan_sub = MPScanRelaxGen(
#             user_potcar_functional="PBE_52",
#             user_incar_settings={"METAGGA": "SCAN"},
#         ).get_input_set(self.struct)
#         incar = mp_scan_sub.incar
#         self.assertEqual(incar["METAGGA"], "Scan")

#     def test_nonmetal(self):
#         # Test that KSPACING and ISMEAR change with a nonmetal structure
#         file_path = self.TEST_FILES_DIR / "POSCAR.O2"
#         struct = Poscar.from_file(file_path, check_for_POTCAR=False).structure
#         scan_nonmetal_set = MPScanRelaxGen().get_input_set(struct, bandgap=1.1)
#         incar = scan_nonmetal_set.incar
#         self.assertAlmostEqual(incar["KSPACING"], 0.3064757, places=5)
#         self.assertEqual(incar["ISMEAR"], -5)
#         self.assertEqual(incar["SIGMA"], 0.05)

#     def test_kspacing_cap(self):
#         # Test that KSPACING is capped at 0.44 for insulators
#         file_path = self.TEST_FILES_DIR / "POSCAR.O2"
#         struct = Poscar.from_file(file_path, check_for_POTCAR=False).structure
#         scan_nonmetal_set = MPScanRelaxGen().get_input_set(struct, bandgap=10)
#         incar = scan_nonmetal_set.incar
#         self.assertAlmostEqual(incar["KSPACING"], 0.44, places=5)
#         self.assertEqual(incar["ISMEAR"], -5)
#         self.assertEqual(incar["SIGMA"], 0.05)

#     def test_incar_overrides(self):
#         # use 'user_incar_settings' to override the KSPACING, ISMEAR, and SIGMA
#         # parameters that MPScanSet normally determines
#         mp_scan_set2 = MPScanRelaxGen(user_incar_settings={"KSPACING": 0.5, "ISMEAR": 0, "SIGMA": 0.05}).get_input_set(
#             self.struct
#         )
#         incar = mp_scan_set2.incar
#         self.assertEqual(incar["KSPACING"], 0.5)
#         self.assertEqual(incar["ISMEAR"], 0)
#         self.assertEqual(incar["SIGMA"], 0.05)

#     # Test SCAN+rVV10
#     def test_rvv10(self):
#         scan_rvv10_set = MPScanRelaxGen(vdw="rVV10").get_input_set(self.struct)
#         self.assertIn("LUSE_VDW", scan_rvv10_set.incar)
#         self.assertEqual(scan_rvv10_set.incar["BPARAM"], 15.7)

#     def test_other_vdw(self):
#         # should raise a warning.
#         # IVDW key should not be present in the incar
#         with pytest.warns(UserWarning, match=r"not supported at this time"):
#             scan_vdw_set = MPScanRelaxGen(vdw="DFTD3").get_input_set(self.struct)
#             self.assertNotIn("LUSE_VDW", scan_vdw_set.incar)
#             self.assertNotIn("IVDW", scan_vdw_set.incar)

#     def test_potcar(self):
#         self.assertEqual(self.mp_scan_set.potcar.functional, "PBE_52")

#         # the default functional should be PBE_54
#         test_potcar_set_1 = MPScanRelaxGen().get_input_set(self.struct)
#         self.assertEqual(test_potcar_set_1.potcar.functional, "PBE_54")

#         with pytest.raises(ValueError):
#             MPScanRelaxGen(user_potcar_functional="PBE").get_input_set(self.struct)

#     def test_as_from_dict(self):
#         vis = self.mp_scan_gen.get_input_set(self.struct)
#         assert isinstance(vis, DictSet)
#         d = self.mp_scan_gen.get_input_set(self.struct).as_dict()
#         v = dec.process_decoded(d)
#         self.assertEqual(type(v), VaspInputSet)
#         self.assertEqual(v._config_dict["INCAR"]["METAGGA"], "R2SCAN")
#         self.assertEqual(v.user_incar_settings["NSW"], 500)

#     def test_write_input(self):
#         self.mp_scan_gen.get_input_set(self.struct).write_input(".")
#         self.assertTrue(os.path.exists("INCAR"))
#         self.assertFalse(os.path.exists("KPOINTS"))
#         self.assertTrue(os.path.exists("POTCAR"))
#         self.assertTrue(os.path.exists("POSCAR"))

#         for f in ["INCAR", "POSCAR", "POTCAR"]:
#             os.remove(f)

#     def test_write_inputs(self):
#         self.mp_scan_gen.get_input_set(self.struct).write_input(".")
#         self.assertTrue(os.path.exists("INCAR"))
#         self.assertFalse(os.path.exists("KPOINTS"))
#         self.assertTrue(os.path.exists("POTCAR"))
#         self.assertTrue(os.path.exists("POSCAR"))

#         for f in ["INCAR", "POSCAR", "POTCAR"]:
#             os.remove(f)

#         self.mp_scan_gen.get_input_set(self.struct).write_input(".", potcar_spec=True)
#         self.assertTrue(os.path.exists("POTCAR.spec"))

#         self.mp_scan_gen.get_input_set(self.struct).write_input(".", include_cif=True)
#         self.assertTrue(os.path.exists("Fe4P4O16.cif"))

#         self.mp_scan_gen.get_input_set(self.struct).write_input(".", zip_output=True)
#         self.assertTrue(os.path.exists("DictSet.zip"))

#         for f in ["POTCAR.spec", "Fe4P4O16.cif", "DictSet.zip"]:
#             os.remove(f)
