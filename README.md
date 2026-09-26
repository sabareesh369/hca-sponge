# HCA-Sponge

A nonlinear three-dimensional cellular-automata (3D-CA) sponge permutation for FPGA hashing.
Research artefact for the paper *"HCA-Sponge: A Nonlinear Three-Dimensional Cellular-Automata
Sponge Permutation with Lane-Dependent Diffusion for FPGA Hashing"* (SASTRA Deemed to be University).

> **Research prototype.** HCA-Sponge is a new, non-standard permutation. It is **not** SHA-3
> (FIPS 202) and has not received independent cryptanalysis. Do not use it in production.

## Design in one paragraph
State: 1600 bits (5x5 lanes of 64 bits), rate 576, capacity 1024, 512-bit digest, Keccak pad10*1.
Each round: theta -> lane-dependent rotation (rho') -> B1..B4 -> iota, where
B1 = rotL1(chi_row(column XOR)), B2 = rotR7(chi_col(row XOR)),
B3 = rotL13(NOT chi_col(chi_row)), B4 = rotR28(chi_diag).
Every step is invertible (verified exhaustively over all 2^25 slice values).

## Repository layout
| Path | Contents |
|---|---|
| `rtl/hca24/` | 24-round core, 32-bit input port (24 cycles/block) |
| `rtl/hca12_64/` | 12-round core, 64-bit input port (12 cycles/block) |
| `rtl/tb/` | Testbenches: known answers, 18 message lengths incl. multi-block, throughput, waveform |
| `model/` | Bit-exact Python model (`sponge.py`, `hca_round.py`) |
| `analysis/` | All security experiments used in the paper |
| `vivado/run_v3.tcl` | Out-of-context implementation of Keccak baseline, HCA-24 and HCA-12 |

## Known-answer tests (first 64 bits)
| Message | HCA-24 | HCA-12 |
|---|---|---|
| `The quick brown fox jumps over the lazy dog` | `bdde89077f1b6982` | `6ca626f5b8249ac9` |
| `The quick brown fox jumps over the lazy dog.` | `813331b61cc53c25` | `a06aa52df6e32ae2` |

## Reproducing the results
```bash
pip install numpy matplotlib pycryptodome
cd analysis && export PYTHONPATH=../model
python bij.py && python bij2.py   # invertibility: parallel (lossy) vs sequential (bijective) equations
python eval3.py                   # avalanche + SAC (512,000 flips), linearity, truncated collisions
python eval4.py                   # ablation (theta / rho') and zero-sum cube test
python diff.py; python track_b.py # differential bias and linear correlation vs Keccak-f
python gen2.py 24                 # 10^8 bits for NIST SP 800-22 (https://github.com/arcetri/sts)
python figs2.py                   # figures
```
RTL simulation (Icarus Verilog):
```bash
iverilog -o t rtl/tb/tb_multilength_64bit.v rtl/hca12_64/*.v && vvp -n t
```

## License
Apache License 2.0. The padder, control and round-constant modules are derived from the
Keccak core by Homer Hsing (OpenCores, Apache-2.0); see `NOTICE`.
