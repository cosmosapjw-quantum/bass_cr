/**
 * @file Coulomb.H
 * @brief Define a class to compute Coulomb losses
 *
 * @author Mark Krumholz
 */

#ifndef _COULOMB_H_
#define _COULOMB_H_

#include <cmath>
#include "LossMechanism.H"
#include "../IO/ParmParser.H"
#include "../Utils/Constants.H"
#include "../Utils/PartTypes.H"

namespace criptic
{

      /**
       * @class Coulomb
       * @brief A class that computes Coulomb losses
       */
      class Coulomb : public LossMechanism
      {

      public:
            /**
             * @brief Mechanism causes continuous loss to a given type?
             * @param type Type of particle
             * @return Whether this mechanism causes continuous loss
             */
            virtual bool ctsLoss(const partTypes::pType type) const override
            {
                  return true;
            }

            /**
             * @brief Compute the continuous loss rate
             * @param gd Background gas data
             * @param packet Cosmic ray packet whose losses are being computed
             * @returns Rate of continuous momentum loss dp/dt
             */
            virtual Real dpdt(const gas::GasData &gd,
                              const CRPacket &packet) const override
            {
                  using namespace constants;
                  Real gamma = packet.gamma();
                  Real beta = packet.v();
                  Real v = beta * c;

                  // Charge number of the incident particle (1 for p/e-/e+,
                  // 5 for boron, 6 for carbon, 7 for nitrogen, 8 for oxygen).
                  // Stored as +/-1 for electron/positron in PartTypes, so use its
                  // magnitude here.
                  Real z = std::abs(static_cast<Real>(partTypes::charge[packet.type]));

#ifdef CRIPTIC_UNITS_CGS
                  Real wp = e *
                            std::sqrt(4 * M_PI * gd.neFree() / me); // plasma frequency
                  Real dEdt_fac = z * z * e * e * wp * wp / v;      // dE/dt in physical units
#else
                  Real wp = e *
                            std::sqrt(gd.neFree() / (me * eps0)); // plasma frequency
                  Real dEdt_fac = z * z * 4 * M_PI * eps0 *
                                  e * e * wp * wp / v; // dE/dt in physical units
#endif

                  // Classical-to-Born interpolation term, eq. (35)-(37) of Krumholz,
                  // Crocker & Sampson (2022), built from Gould (1972).
                  Real Bfac = 0.5 * std::log(1 + (GammaC * beta / alpha) *
                                                     (GammaC * beta / alpha));

                  Real Bstop;
                  switch (packet.type)
                  {
                  case partTypes::proton:
                  case partTypes::boron10:
                  case partTypes::boron11:
                  case partTypes::carbon12:
                  case partTypes::nitrogen14:
                  case partTypes::oxygen16:
                  {
                        // Relativistic heavy-ion Coulomb stopping number, eq. (35) of
                        // Krumholz, Crocker & Sampson (2022), generalized from protons
                        // to boron/carbon/nitrogen/oxygen via the z factor above.
                        Bstop = std::log(2 * gamma * me_c2 * beta * beta /
                                         (hBar * wp)) -
                                beta * beta / 2 + Bfac;
                        break;
                  }
                  case partTypes::electron:
                  {
                        Real gamm1 = gamma - 1;
                        Real gam2 = gamma * gamma;
                        Bstop =
                            std::log(std::sqrt(2 * delta * (gamma - 1)) *
                                     beta * me_c2 / (hBar * wp)) +
                            Bfac + 0.5 * ((1 + (2 * gamma - 1) / gam2) * std::log(1 - delta) + delta / (1 - delta)) + 0.25 * delta * delta * gamm1 * gamm1 / gam2;
                        break;
                  }
                  case partTypes::positron:
                  {
                        Real gamm1 = gamma - 1;
                        Real gamp1 = gamma + 1;
                        Real gam2 = gamma * gamma;
                        Bstop =
                            std::log(std::sqrt(2 * delta * (gamma - 1)) *
                                     beta * me_c2 / (hBar * wp)) +
                            Bfac + 0.25 * delta * delta * gamm1 * gamm1 / (gamp1 * gamp1) * (0.5 + 1 / gamma + 3 / (2 * gam2) - gamm1 * gamm1 / gam2 * (2 * delta / 3 - delta * delta / 2)) + delta * (delta / 8 * gamm1 * gamm1 / gam2 - (gam2 - 1) / (2 * gam2)) - 0.5 * delta * gamm1 / gamp1 * ((gamma + 2) / gamma - (gam2 - 1) / gam2 * delta + gamm1 * gamm1 / gam2 * delta * delta / 3);
                        break;
                  }
                  default:
                  {
                        // Never get here
                        Bstop = 0.0;
                  }
                  }
                  Real dEdt = dEdt_fac * Bstop;
                  return (dEdt / constants::mp_c2) / packet.dT_dp();
            }

      private:
            // Constants
            static constexpr Real
                GammaC = 0.5615; /**< Plasma loss parameter */
            static constexpr Real
                delta = 0.5; /**< Electron plasma loss parameter */
      };
}

#endif
// _COULOMB_H_
