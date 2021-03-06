/*******************************************************************************
* File:        Byte_buffer.h
* Description: Implementation of a Byte buffer
*
* Author:      Chris Newton
* Created:     Thursday 1 December 2016
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

#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include "Hex_string.h"

using Byte = unsigned char;
using Byte_ptr = Byte *;
using Byte_const_ptr = Byte const *;
constexpr unsigned int hex_base{ 16 };
constexpr unsigned int byte_base{ 256 };

class Byte_buffer
{
  public:
    using Bytes = std::vector<Byte>;
    static constexpr uint32_t initial_reserved_size = 32;
    Byte_buffer();
    Byte_buffer(Byte_buffer const &bb) = default;
    Byte_buffer(Byte_buffer &&bb) = default;
    Byte_buffer &operator=(Byte_buffer const &bb) = default;
    explicit Byte_buffer(std::initializer_list<Byte> il);
    explicit Byte_buffer(Bytes bv);
    explicit Byte_buffer(size_t sz);
    Byte_buffer(size_t sz, Byte const &b);
    explicit Byte_buffer(Hex_string const &hs);// Every two hex characters are one Byte
    explicit Byte_buffer(std::string const &str);// Each character is one Byte
    Byte_buffer(Byte const *buf, size_t len);
    Byte &operator[](size_t pos) { return byte_buf_[pos]; }
    Byte const &operator[](size_t pos) const { return byte_buf_[pos]; }
    Byte_buffer get_part(size_t start, size_t length) const;
    void set_part(size_t start, Byte_buffer const &part);
    Byte_buffer &operator+=(Byte_buffer const &b);
    bool operator==(Byte_buffer const &rhs) const { return byte_buf_ == rhs.byte_buf_; }
    bool operator!=(Byte_buffer const &rhs) const { return byte_buf_ != rhs.byte_buf_; }
    bool operator<(Byte_buffer const &rhs) const { return byte_buf_ < rhs.byte_buf_; }
    void resize(size_t n) { byte_buf_.resize(n); }
    void reserve(size_t n) { byte_buf_.reserve(n); }
    void push_back(Byte b) { byte_buf_.push_back(b); }
    bool empty() const { return byte_buf_.empty(); }
    void clear() { byte_buf_.clear(); }
    Byte_ptr data() { return byte_buf_.data(); }
    Byte_const_ptr cdata() const { return byte_buf_.data(); }
    size_t size() const { return byte_buf_.size(); }
    void pad_right(size_t new_length, Byte b = 0);
    void pad_left(size_t new_length, Byte b = 0);
    void truncate();
    std::string to_hex_string() const;
    friend std::istream &operator>>(std::istream &is, Byte_buffer &bb);
    ~Byte_buffer() = default;

  private:
    Bytes byte_buf_;

    //    void initialise();
};

Byte_buffer operator+(Byte_buffer const &a, Byte_buffer const &b);

// Reads a Byte_buffer from the input stream. The input should be an even number of hex characters
// terminated with whitespace NOT just with some non-hex character
std::istream &operator>>(std::istream &is, Byte_buffer &bb);

// Outputs a Byte_buffer as a hex string with NO whitespace at the end
std::ostream &operator<<(std::ostream &os, Byte_buffer const &bb);

// Outputs a Byte_buffer as a string. Apart from terminating whitespace or nulls,
// non-printable charcters are replaced with ?
void print_bb_as_characters(std::ostream &os, Byte_buffer const &bb);

Byte_buffer uint16_to_bb(uint16_t ui);

Byte_buffer uint32_to_bb(uint32_t ui);

std::string bb_to_string(Byte_buffer const &bb);

Byte_buffer serialise_bb(Byte_buffer const &bb);

Byte_buffer deserialise_bb(Byte_buffer const &bb);

Byte_buffer serialise_byte_buffers(std::vector<Byte_buffer> const &bbs);

std::vector<Byte_buffer> deserialise_byte_buffers(Byte_buffer const &bb);
