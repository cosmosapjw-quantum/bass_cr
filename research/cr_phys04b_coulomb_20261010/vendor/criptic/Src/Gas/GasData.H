/**
 * @file GasData.H
 * @brief Class to describe the background gas at a single point
 *
 * @author Mark Krumholz
 */

#ifndef _GASDATA_H_
#define _GASDATA_H_

#include <cmath>
#include <vector>
#include "../Utils/Constants.H"
#include "../Utils/Types.H"
#include "../Utils/RealTensor2.H"
#include "../Utils/Vec3.H"

namespace criptic {

  namespace gas {

    /**
     * @brief Trivial class to hold gas data
     * @details
     * This class holds information about the gas density, velocity,
     * magnetic field, and their gradients. It provides some trivial
     * utility methods.
     */
    class GasData {

    public:
      
      Real dx;             /**< Characteristic length scale */

      // Quantities
      Real den;            /**< Total mass density */
      Real ionDen;         /**< Ionized mass density */
      RealVec v;           /**< Gas velocity */
      RealVec B;           /**< Magnetic field */

      // Gradients of quantities
      RealVec denGrad;     /**< Total density gradient */
      RealVec ionDenGrad;  /**< Ionized density gradient */
      RealTensor2 vGrad;   /**< Velocity gradient, dv_i / dx_j */
      RealTensor2 BGrad;   /**< Gradient of magnetic field, dB_i / dx_j */

      // Composition information -- needed for loss calculations
      Real xH0;            /**< H^0 abundance per H nucleon */
      Real xHp;            /**< H^+ abundance per H nucleon */
      Real xHe0;           /**< He^0 abundance per H nucleon */
      Real xHep;           /**< He^+ abundance per H nucleon */
      Real xHep2;          /**< He^++ abundance per H nucleon */
      Real xe;             /**< Free electron abundance per H nucleon */
      Real Z;              /**< Heavy element abundance by mass */
      
      // Radiation field information -- needed for inverse Compton losses
      std::vector<Real> TBB; /**< Temperatures of BB radiation fields */
      std::vector<Real> WBB; /**< Dilution factors of BB radiation fields */

      // Trivial convenience methods
      /**
       * @brief Compute magnetic energy density
       * @returns Magnetic energy density
       * @details
       * This method correctly computes the magnetic energy density in
       * either Gaussian or SI units, depending on which are
       * selected at compile-time.
       */
      Real UB() const {
#ifdef CRIPTIC_UNITS_CGS
	return B.mag2() / (8 * M_PI);
#else
	return B.mag2() / (2 * constants::mu0);
#endif
      }

      /**
       * @brief Compute H2 abundance
       * @returns H2 abundance
       * @details
       * This method deduces the H2 abundance from the HI and HII
       * abundances.
       */
      constexpr Real xH2() const {
	return 0.5 * (1 - xH0 - xHp);
      }

      /**
       * @brief Compute total He abundance across all ionization states
       * @returns Total He abundance
       */
      constexpr Real xHe() const {
	return xHe0 + xHep + xHep2;
      }
      
      /**
       * @brief Compute H abundance by mass
       * @returns H abundance by mass
       */
      constexpr Real X() const {
	return (1.0 - Z) / (1.0 + 4.0 * (xHe0 + xHep + xHep2));
      }

      /**
       * @brief Compute He abundance by mass
       * @returns He abundance by mass
       */
      constexpr Real Y() const {
	return (1.0 - Z) * 4.0 * xHe() / (1.0 + 4.0 * xHe());
      }

      /**
       * @brief Return heavy element abundance times mean atomic mass
       * @returns A_mean * x_Z
       * @details
       * This routine returns the mean atomic mass A_mean of
       * heavy elements multiplied by the heavy element abundance per
       * H, x_Z
       */
      constexpr Real AxZ() const {
	return (1.0 + 4.0 * xHe()) * Z / (1.0 - Z);
      }

      /**
       * @brief Compute mean mass per H nucleon
       * @returns Mass per H nucleon, in units of the H atom mass
       */
      constexpr Real muH() const {
	return 1.0 / X();
      }

      /**
       * @brief Compute mean mass per electron
       * @returns Mass per electron, in units of the H atom mass
       * @details
       * This calculation assumes heavy elements have a number of
       * electrons equal to half their atomic mass
       */
      constexpr Real mue() const {
	return (1.0 + 4.0 * xHe() + AxZ()) /
	  (1.0 + 2.0 * xHe() + 0.5 * AxZ());
      }

      /**
       * @brief Compute number density of H nuclei
       * @returns Number density of H nuclei
       */
      constexpr Real nH() const {
	return den / (muH() * constants::mH);
      }

      /**
       * @brief Compute total number density of electrons
       * @returns Total number density of electrons
       * @details
       * Here "total" means the number density of all electrons, free
       * or bound.
       */
      constexpr Real neTot() const {
	return den / (mue() * constants::mH);
      }
      
      /**
       * @brief Compute number density of free electrons
       * @returns Number density of free electrons
       */
      constexpr Real neFree() const {
	return xe * nH();
      }
      
      /**
       * @brief Set reasonable abundances for atomic ISM
       * @details He and metal abundances taken from Asplund+ (2009)
       */
      void setAtomicComposition() {
	xH0 = 1.0 - 1.0e-2;
	xHp = xe = 1.0e-2;
	xHe0 = 0.0955;
	xHep = xHep2 = 0.0;
	Z = 0.0199;
      }
      
      /**
       * @brief Set reasonable abundances for molecular ISM
       * @details He and metal abundances taken from Asplund+ (2009)
       */
      void setMolecularComposition() {
	xH0 = xHp = 0.0;
	xe = 1.0e-6;
	xHe0 = 0.0955;
	xHep = xHep2 = 0.0;
	Z = 0.0199;
      }

      /**
       * @brief Set reasonable abundances for fully ionized ISM
       * @details He and metal abundances taken from Asplund+ (2009)
       */
      void setIonizedComposition() {
	xH0 = xHe0 = 0.0;    // No neutral species
	xHp = 1.0;           // H is fully ionized
	xHep = 0.0;          // Treat He as fully ionized
	xHep2 = 0.0955;
	xe = 1 + 2 * 0.0955; // Asplund+ (2009) He abundance, fully ionized
	Z = 0.0199;
      }

      // Define the the operations of multiplication by a scalar and
      // addition of two GasData object. These are intended to make it
      // possible to take weighted averages of GasData objects.

      /**
       * @fn criptic::gas::GasData::operator*(const criptic::Real&) const
       * @brief Multiply by a scalar
       * @param w The scalar
       * @return A GasData object with every field multiplied by w
       * @details
       * For the blackbody radiation field, the dilution factor is
       * multiplied by w, but the temperature is left unchanged.
       */
      GasData operator*(const Real& w) const {
	GasData r;
	r.dx = w * dx;
	r.den = w * den;
	r.ionDen = w * ionDen;
	r.v = w * v;
	r.B = w * B;
	r.denGrad = w * denGrad;
	r.ionDenGrad = w * ionDenGrad;
	r.vGrad = w * vGrad;
	r.BGrad = w * BGrad;
	r.xH0 = w * xH0;
	r.xHp = w * xHp;
	r.xHe0 = w * xHe0;
	r.xHep = w * xHep;
	r.xHep2 = w * xHep2;
	r.xe = w * xe;
	r.Z = w * Z;
	r.WBB = WBB;
	for (IdxType i=0; i<WBB.size(); i++) r.WBB[i] *= w;
	r.TBB = TBB;
	return r;
      }

      /**
       * @fn criptic::gas::GasData::operator+(const criptic::gas::GasData&) const
       * @brief Add two GasData objects
       * @param gd The GasData object to add
       * @return A GasData object consisting of the sum of the two inputs
       * @details
       * For the blackbody radiation components, the dilution factors
       * are added, and the blackbody temperatures are unchanged. If
       * the blackbody temperatures of the two objects being added are
       * not elementwise identical, the outcome is undefined.
       */
      GasData operator+(const GasData& gd) const {
	GasData r;
	r.dx = gd.dx + dx;
	r.den = gd.den + den;
	r.ionDen = gd.ionDen + ionDen;
	r.v = gd.v + v;
	r.B = gd.B + B;
	r.denGrad = gd.denGrad + denGrad;
	r.ionDenGrad = gd.ionDenGrad + ionDenGrad;
	r.vGrad = gd.vGrad + vGrad;
	r.BGrad = gd.BGrad + BGrad;
	r.xH0 = gd.xH0 + xH0;
	r.xHp = gd.xHp + xHp;
	r.xHe0 = gd.xHe0 + xHe0;
	r.xHep = gd.xHep + xHep;
	r.xHep2 = gd.xHep2 + xHep2;
	r.xe = gd.xe + xe;
	r.Z = gd.Z + Z;
	r.WBB = gd.WBB;
	for (IdxType i=0; i<WBB.size(); i++) r.WBB[i] += WBB[i];
	r.TBB = TBB;
	return r;
      }      
    };

    // Scalar multiplication and addition operators
    /**
     * @brief Multiply a GasData object by a scalar
     * @param w The scalar
     * @param gd The GasData object
     * @return A GasData object with every field of gd multiplied by w
     * @details
     * The blackbody dilution factors are mulitplied by w, but the
     * blackbody temperatures are left unchanged
     */
    inline GasData operator*(const Real& w,
			     const GasData& gd) {
      return gd * w;
    }
  }
}

#endif
// _GASDATA_H_
