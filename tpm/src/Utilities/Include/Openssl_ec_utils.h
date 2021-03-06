/*******************************************************************************
* File:        Openssl_ec_utils.h
* Description: Utility functions for Openssl EC
*
* Author:      Chris Newton
* Created:     Wednesday 20 June 2018
*
*
*******************************************************************************/

/*******************************************************************************
*                                                                              *
* (C) Copyright 2020-2021 University of Surrey                                 *
*                                                                              *
* Redistribution and use in source and binary forms, with or without           *
* modification, are permitted provided that the following conditions are met:  *
*                                                                              *
* 1. Redistributions of source code must retain the above copyright notice,    *
* this list of conditions and the following disclaimer.                        *
*                                                                              *
* 2. Redistributions in binary form must reproduce the above copyright notice, *
* this list of conditions and the following disclaimer in the documentation    *
* and/or other materials provided with the distribution.                       *
*                                                                              *
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"  *
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE    *
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE   *
* ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE    *
* LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR          *
* CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF         *
* SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS     *
* INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN      *
* CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)      *
* ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   *
* POSSIBILITY OF SUCH DAMAGE.                                                  *
*                                                                              *
*******************************************************************************/

#pragma once 

#include <cstdint>
#include <string>
#include <iostream>
#include <memory>
#include <vector>
#include <openssl/err.h>
#include <openssl/bn.h>
#include <openssl/ec.h>
#include "G1_utils.h"
#include "Openssl_bn_utils.h"
#include "Byte_buffer.h"

using Ec_group_ptr=std::unique_ptr<EC_GROUP,decltype(&::EC_GROUP_free)>;
Ec_group_ptr new_ec_group(std::string const& curve_name);

using Ec_key_ptr=std::unique_ptr<EC_KEY,decltype(&::EC_KEY_free)>;
Ec_key_ptr new_ec_key();

using Ec_point_ptr=std::unique_ptr<EC_POINT,decltype(&::EC_POINT_free)>;
Ec_point_ptr new_ec_point(Ec_group_ptr const& ecgrp);
// Openssl get0 functions return a const pointer and do not affect 
// the reference counting - these pointers must not be freed - no unique_ptr 
using Ec_point_ptr0=EC_POINT const*;

using Ec_key_pair_bb=std::pair<Byte_buffer,G1_point>;

G1_point point2bb(Ec_group_ptr const& ecgrp, Ec_point_ptr const& point);
G1_point point2bb0(Ec_group_ptr const& ecgrp, Ec_point_ptr0 point);

void bb2point(Ec_group_ptr const& ecgrp,G1_point const& pt_bb, Ec_point_ptr& pt);

bool point_is_on_curve(Ec_group_ptr const& ecgrp,G1_point const& pt_bb);

bool point_is_at_infinity(Ec_group_ptr const& ecgrp,G1_point const& pt_bb);

G1_point ec_point_add(
Ec_group_ptr const& ecgrp,
G1_point const& pt_a_bb,
G1_point const& pt_b_bb
);

G1_point ec_generator_mul(
Ec_group_ptr const& ecgrp,
Byte_buffer const& multiplier
);

G1_point ec_point_mul(
Ec_group_ptr const& ecgrp,
Byte_buffer const& multiplier,
G1_point const& pt_bb);

G1_point ec_point_invert(
Ec_group_ptr const& ecgrp,
G1_point const& pt_bb
);

Ec_key_pair_bb get_new_key_pair(
Ec_group_ptr const& ecgrp
);

bool verify_ecdsa_signature(
std::string curve_name,
G1_point const& ecdsa_public_key,
Byte_buffer const& digest_to_sign,
Byte_buffer const& sigR,
Byte_buffer const& sigS
);
