/**
 * @file Constants.H
 * @brief Data file of physical constants
 *
 * @details
 * This file provides a namespace that holds physical constants. These
 * are stored in eihter CGS or MKS units, depending on the option
 * selected at compile time.
 *
 * @author Mark Krumholz
 */

#ifndef _CONSTANTS_H_
#define _CONSTANTS_H_

#include <gsl/gsl_const_cgsm.h>
#include <gsl/gsl_const_mksa.h>
#include <gsl/gsl_const_num.h>
#include "../Definitions.H"
#include "Types.H"
#include "Units.H"

namespace criptic {

  /**
   * @brief A namespace to hold physcial constants.
   */
  namespace constants {
    
#ifdef CRIPTIC_UNITS_CGS
  
    // CGS units
    static constexpr Real c
    = GSL_CONST_CGSM_SPEED_OF_LIGHT;  /**< Speed of light */
    static constexpr Real mp
    = GSL_CONST_CGSM_MASS_PROTON;     /**< Proton mass */
    static constexpr Real me
    = GSL_CONST_CGSM_MASS_ELECTRON;   /**< Electron  mass */
    static constexpr Real sigmaT
    = GSL_CONST_CGSM_THOMSON_CROSS_SECTION;  /**< Thomson cross section */
    static constexpr Real kB =
      GSL_CONST_CGSM_BOLTZMANN;       /**< Boltzmann's constant */
    static constexpr Real h =
      GSL_CONST_CGSM_PLANCKS_CONSTANT_H;  /**< Planck's constant */
    static constexpr Real hBar =
      GSL_CONST_CGSM_PLANCKS_CONSTANT_HBAR;  /**< Planck's constant / 2 pi */
    static constexpr Real e =
      GSL_CONST_CGSM_ELECTRON_CHARGE * c; /**< Electron charge -- note
					     the factor of c, needed because
					     the GSL's version of cgs
					     uses electromagnetic
					     units (EMU) rather than
					     Gaussian units; the
					     factor of c converts
					     from abCoulomb (EMU) to
					     statCoulomb (Gaussian) */
    static constexpr Real a0 =
      GSL_CONST_CGSM_BOHR_RADIUS; /**< Bohr radius */
    static constexpr Real Ryd =
      GSL_CONST_CGSM_RYDBERG; /**< Rydberg energy */
    static constexpr Real sigmaSB =
      GSL_CONST_CGSM_STEFAN_BOLTZMANN_CONSTANT; /**< Stefan-Boltzmman constant */
    static constexpr Real r0 =
      e * e / (me * c * c); /**< Classical electron radius */
    static constexpr Real Msun =
      GSL_CONST_CGSM_SOLAR_MASS; /**< Mass of the Sun */
    static constexpr Real Lsun =
      3.828e33; /**< Luminosity of the Sun -- IAU 2015 value */
    static constexpr Real amu = 
      GSL_CONST_CGSM_UNIFIED_ATOMIC_MASS; /**< Atomic mass unit */
    
#elif defined(CRIPTIC_UNITS_MKS)

    // MKS units
    static constexpr Real c
    = GSL_CONST_MKSA_SPEED_OF_LIGHT;  /**< Speed of light */
    static constexpr Real mp
    = GSL_CONST_MKSA_MASS_PROTON;     /**< Proton mass */
    static constexpr Real me
    = GSL_CONST_MKSA_MASS_ELECTRON;   /**< Electron mass */
    static constexpr Real sigmaT
    = GSL_CONST_MKSA_THOMSON_CROSS_SECTION;  /**< Thomson cross section */
    static constexpr Real kB =
      GSL_CONST_MKSA_BOLTZMANN;         /**< Boltzmann's constant */  
    static constexpr Real h =
      GSL_CONST_MKSA_PLANCKS_CONSTANT_H;  /**< Planck's constant */
    static constexpr Real hBar =
      GSL_CONST_MKSA_PLANCKS_CONSTANT_HBAR;  /**< Planck's constant / 2 pi */
    static constexpr Real e =
      GSL_CONST_MKSA_ELECTRON_CHARGE; /**< Electron charge */
    static constexpr Real a0 =
      GSL_CONST_MKSA_BOHR_RADIUS; /**< Bohr radius */
    static constexpr Real Ryd =
      GSL_CONST_MKSA_RYDBERG; /**< Rydberg energy */
    static constexpr Real sigamSB =
      GSL_CONST_MKSA_STEFAN_BOLTZMANN_CONSTANT; /** Stefan-Boltzmman constant */
    static constexpr Real eps0 =
      GSL_CONST_MKSA_VACUUM_PERMITTIVITY; /**< Vacuum permittivity */
    static constexpr Real mu0 =
      GSL_CONST_MKSA_VACUUM_PERMEABILITY;  /**< Vacuum permeability */
    static constexpr Real r0 =
      e * e / (4.0 * M_PI * eps0 * me * c * c); /**< Classical electron radius */
    static constexpr Real Msun =
      GSL_CONST_MKSA_SOLAR_MASS; /**< Mass of the Sun */
    static constexpr Real Lsun =
      3.828e26; /**< Luminosity of the Sun -- IAU 2015 value */
    static constexpr Real amu = 
      GSL_CONST_MKSA_UNIFIED_ATOMIC_MASS; /**< Atomic mass unit */
    
#endif

    // Additional constants derived from the above
    static constexpr Real c2 = c*c;        /**< Speed of light squared */
    static constexpr Real c3 = c*c*c;      /**< Speed of light cubed */
    static constexpr Real e2 = e*e;        /**< Electron charge squared */
    static constexpr Real e3 = e*e*e;      /**< Electron charge cubed */
    static constexpr Real mp_c = mp * c;   /**< Proton mass times c */
    static constexpr Real mp_c2 = mp * c2; /**< Proton rest energy */
    static constexpr Real me_c = me * c;   /**< Electrons mass times c */
    static constexpr Real me_c2 = me * c2; /**< Electron rest energy */
    static constexpr Real alpha = 
      GSL_CONST_NUM_FINE_STRUCTURE; /**< Fine structure constant */
    static constexpr Real aR = 4.0 * sigmaSB / c; /**< Radiation constant */
    
    // Particle masses and related quantities -- from CODATA 2018
    static constexpr Real mPi0 = 134.9758 * units::MeV / c2; /**< pi^0 mass */
    static constexpr Real mPic = 139.57061 * units::MeV / c2; /**< pi^+- mass */
    static constexpr Real mMu = 105.6583755 * units::MeV / c2; /**< Muon mass */
    static constexpr Real Tpth = 2 * mPi0 * c2 +
      mPi0 * c2 * mPi0 * c2 /
      (2 * mp_c2); /**< Threshold proton KE for pp -> pp pi^0 */
    static constexpr Real rMuPi = mMu / mPic; /**< Mass ratio for
						 pi^+- / mu */

    // Masses of astrophysically-important light isotopes -- all taken from
    // https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl. Note
    // the namine convention for isotopes: mXn is the mass of the isotope of
    // element X with atomic number n. When one isotope is overwhelmingly
    // dominant, for example carbon 12, mX without the trailing number gives
    // the mass of the dominant isotope. The only except to this is for
    // hydrogen, where the mass of deuterium is mDeut -- this is to avoid
    // the confusion that would result from calling it mH2, which could be
    // either the mass of deuterium, or of the H2 molecule.
    static constexpr Real mH = 1.007825032239 * amu; /**< Hydrogen mass */
    static constexpr Real mDeut = 2.0141017781212 * amu; /**< Deuterium mass */
    static constexpr Real mHe3 = 3.016029320125 * amu; /**< He-3 mass */ 
    static constexpr Real mHe4 = 4.002603254136 * amu; /**< He-4 mass */
    static constexpr Real mHe = mHe4; /**< He mass */
    static constexpr Real mLi6 = 6.015122887416 * amu; /**< Li-6 mass */ 
    static constexpr Real mLi7 = 7.016003436645 * amu; /**< Li-7 mass */ 
    static constexpr Real mBe = 9.01218306582 * amu; /**< Be mass */ 
    static constexpr Real mB10 = 10.0129369541 * amu; /**< B-10 mass */ 
    static constexpr Real mB11 = 11.0093053645 * amu; /**< B-11 mass */ 
    static constexpr Real mC12 = 12.0 * amu; /**< C-12 mass */
    static constexpr Real mC13 = 13.0033548350723 * amu; /**< C-13 mass */
    static constexpr Real mC14 = 14.003241988440 * amu; /**< C-14 mass */
    static constexpr Real mC = mC12; /**< C mass */
    static constexpr Real mN14 = 14.0030740044320 * amu; /**< N-14 mass */
    static constexpr Real mN15 = 15.0001088988864 * amu; /**< N-15 mass */
    static constexpr Real mN = mN14;
    static constexpr Real mO16 = 15.9949146195717 * amu; /**< O-16 mass */
    static constexpr Real mO17 = 16.9991317565069 * amu; /**< O-17 mass */
    static constexpr Real mO18 = 17.9991596128676 * amu; /**< O-18 mass */
    static constexpr Real mO = mO16; /**< O mass */

    // Nuclear binding energies -- in units of mp c²
    static constexpr Real BE_carbon12 = 92.16175014 * units::MeV / constants::mp_c2;
    static constexpr Real BE_boron10 = 64.7507 * units::MeV / constants::mp_c2;   
    static constexpr Real BE_nitrogen14 = 104.658 * units::MeV / constants::mp_c2;
    static constexpr Real BE_boron11 = 76.204 * units::MeV / constants::mp_c2;
    static constexpr Real BE_oxygen16 = 127.619 * units::MeV / constants::mp_c2;
  }
}


#endif
// _CONSTANTS_H_
