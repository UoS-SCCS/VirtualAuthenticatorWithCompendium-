# Compendium Project
This repository is part of the Compendium Project that built a proof of concept for leveraging the biometric security capabilities found on mobile devices for desktop/laptop security. The project developed a number of protocols and applications to provide a general purpose framework for storing and accessing biometrically protected credentials on a mobile device. A security analysis of the protocols has been undertaken using Tamarin.

The project developed both the backend services and an Android demonstrator app. The framework has been integrated with our previously developed virtual authenticator to show the use of biometrics for secure storage of data on the PC and for performing a biometrically protected user verification.

The list of relevant repositories is as follows:
* [Compendium Library](https://github.com/UoS-SCCS/Compendium-Library) - Provides the Python library to be included by the PC based app that wishes to use the protocol
* [Compendium App](https://github.com/UoS-SCCS/Compendium-Android) - The Android app that provides the companion device functionality
* [Compendium PushServer](https://github.com/UoS-SCCS/Compendium-PushServer) - Provides back-end functionality for the communications protocol
* [Virtual Authenticator with Compendium](https://github.com/UoS-SCCS/VirtualAuthenticatorWithCompendium-) - An extension of development Virtual Authenticator which includes Compendium for secure storage of config data and user verification
* [Security Models](https://github.com/UoS-SCCS/Companion-Device---Tamarin-Models-) - Tamarin security models of the protocol

# Virtual WebAuthn Authenticator with Compendium
This contains an updated verion of the Virtual WebAuthn Authenticator integrated the Compendium companion device for encryption and user verification.


This repository contains the development of a Virtual CTAP2 WebAuthn authenticator. The authenticator is intended to provide a platform for testing and development of WebAuthn/CTAP2 protocols and extensions.

It provides a code base for two kinds of authenticators. Firstly, a software only authenticator, second, a proof of concept implementation of a Trusted Platform Module (TPM) based authenticator, with associated interfaces and libraries for using a TPM as the underlying credential store. It is the first in a series of open source contributions that we will make in the area of WebAuthn authenticator platforms.

There is documentation within the code repository and an accompanying technical report on [Arxiv](http://arxiv.org/abs/2108.04131).

The code was produced as part of the [EPSRC project](https://gow.epsrc.ukri.org/NGBOViewGrant.aspx?GrantRef=EP/N028295/1) that focused on Data to Improve the Customer Experience (DICE). The project's main application domain was intelligent transport systems (ITS) but the scope included ensuring security and data privacy when using web services, for example in the case of [smart ticketing](https://doi.org/10.1109/TDSC.2019.2940946) and [emerging technologies](https://doi.org/10.1007/978-3-030-64455-0_2) that could be applicable in the ITS domain.

Development Team:
* Chris Culnane,
* Chris Newton
* Helen Treharne

## Setup
Setup instructions for the TPM and the Virtual Authenticator are available as follows:
* [TPM Setup](./tpm/README.md)
* [Compendium Setup](./compendiumsetup.md)
* [Virtual Authenticator Setup](./SETUP.md)
