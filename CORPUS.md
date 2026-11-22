# Literature corpus

The 46 works of the systematization in Section 4 of the paper, grouped by category. "Origin" gives the stage of Section 2.1 at which each work was found: the seed set, backward snowballing, or forward snowballing and targeted search.

| # | Category | Work | Year | Venue or channel | Origin |
| --- | --- | --- | --- | --- | --- |
| 1 | Standard | FIPS 205, SLH-DSA | 2024 | NIST | Seed |
| 2 | Standard | SP 800-208, stateful HBS | 2020 | NIST | Backward |
| 3 | Standard | SP 800-230 initial public draft | 2026 | NIST | Seed |
| 4 | Standard | RFC 8391, XMSS | 2018 | IRTF | Backward |
| 5 | Standard | RFC 8554, LMS | 2019 | IRTF | Backward |
| 6 | Framework and proof | SPHINCS | 2015 | EUROCRYPT | Backward |
| 7 | Framework and proof | SPHINCS+ framework | 2019 | ACM CCS | Backward |
| 8 | Framework and proof | Tight proof of SPHINCS+ | 2022 | ASIACRYPT | Backward |
| 9 | Framework and proof | Machine-checked XMSS and SPHINCS+ | 2023 | CRYPTO | Backward |
| 10 | Framework and proof | Formally verified tight proof | 2024 | ASIACRYPT | Backward |
| 11 | One-time scheme | SPHINCS+C: WOTS+C and FORS+C | 2023 | IEEE S&P | Backward |
| 12 | One-time scheme | Constant-sum Winternitz OTS | 2023 | CRYPTO | Backward |
| 13 | One-time scheme | TL-WOTS-TW | 2025 | CRYPTO | Backward |
| 14 | One-time scheme | WOTS-Tree for Bitcoin | 2026 | ePrint 2026/374 | Forward |
| 15 | Few-time scheme | Subset resilience | 2017 | ePrint | Backward |
| 16 | Few-time scheme | PORS and Octopus | 2018 | CT-RSA | Backward |
| 17 | Few-time scheme | Forced pruning, PORS+FP | 2026 | CRYPTO | Backward |
| 18 | Few-time scheme | Bucket thinning, BPORS+FP | 2026 | ePrint 2026/1328 | Seed |
| 19 | Few-time scheme | Hash chains and blockwise pruning | 2026 | ePrint 2026/2374 | Seed |
| 20 | Few-time scheme | Guarded sharing in a DAG model | 2026 | ePrint 2026/2502 | Forward |
| 21 | Few-time scheme | Prepared episodes | 2026 | ePrint 2026/1708 | Forward |
| 22 | Parameter study | Optimal parameters for XMSSMT | 2017 | ePrint | Backward |
| 23 | Parameter study | A note on SPHINCS+ parameter sets | 2022 | ePrint 2022/1725 | Backward |
| 24 | Parameter study | Smaller SPHINCS+ | 2024 | ePrint 2024/018 | Backward |
| 25 | Parameter study | Smaller SLH-DSA parameter sets | 2025 | NIST presentation | Backward |
| 26 | Parameter study | Varying tree heights and chain lengths | 2026 | ASIACRYPT | Backward |
| 27 | Blockchain | Hash-based signatures for Bitcoin | 2025 | ePrint 2025/2203 | Seed |
| 28 | Blockchain | Blockchained post-quantum signatures, BPQS | 2018 | IEEE iThings 2018 | Forward |
| 29 | Blockchain | Stateful hash-based signatures for Bitcoin | 2019 | ICECCO | Forward |
| 30 | Blockchain | SHRINCS proposal | 2025 | Delving Bitcoin | Forward |
| 31 | Blockchain | SHRINCS draft specification | 2026 | bitcoin-dev | Forward |
| 32 | Blockchain | SHRIMPS | 2026 | Delving Bitcoin | Forward |
| 33 | Blockchain | Searching for SHRINCS parameters | 2026 | Blockstream blog | Forward |
| 34 | Blockchain | OP_CHECKSHRINCS | 2026 | Blockstream blog | Forward |
| 35 | Blockchain | BIP 360, Pay-to-Merkle-Root | 2026 | BIP repository | Forward |
| 36 | Blockchain | Poqeth, post-quantum verification on Ethereum | 2025 | ASIA CCS | Forward |
| 37 | Blockchain | SPHINCS-minus on the EVM | 2026 | ethresear.ch | Forward |
| 38 | Blockchain | Ephemeral hash-based keys with account abstraction | 2026 | ethresear.ch | Forward |
| 39 | Blockchain | WOTS-39 wallet | 2026 | Ethereum Magicians | Forward |
| 40 | Blockchain | Ethereum post-quantum roadmap | 2026 | pq.ethereum.org | Backward |
| 41 | Blockchain | Domain-specific PQ signatures for blockchains | 2026 | arXiv 2609.24689 | Forward |
| 42 | Consensus, threshold, and state management | Hash-based multi-signatures for Ethereum | 2025 | IACR CiC | Backward |
| 43 | Consensus, threshold, and state management | LeanSig | 2025 | ePrint 2025/1332 | Backward |
| 44 | Consensus, threshold, and state management | Distributed and threshold HBS | 2025 | IACR CiC | Backward |
| 45 | Consensus, threshold, and state management | PRAWNS threshold HBS | 2026 | ePrint 2026/2142 | Forward |
| 46 | Consensus, threshold, and state management | Hash-based Signatures: State and Backup Management | 2026 | IETF RFC | Backward |

## Full references

1. National Institute of Standards and Technology, "Stateless hash-based digital signature standard," FIPS 205, Aug. 2024. http://doi.org/10.6028/NIST.FIPS.205
2. D. A. Cooper, D. C. Apon, Q. H. Dang, M. S. Davidson, M. J. Dworkin, and C. A. Miller, "Recommendation for stateful hash-based signature schemes," NIST Special Publication 800-208, Oct. 2020. http://doi.org/10.6028/NIST.SP.800-208
3. D. Moody and Q. Dang, "Additional SLH-DSA parameter sets for limited-signature use cases," NIST Special Publication 800-230 (Initial Public Draft), Apr. 2026. http://doi.org/10.6028/NIST.SP.800-230.ipd
4. A. Hülsing, D. Butin, S. Gazdag, J. Rijneveld, and A. Mohaisen, "XMSS: eXtended Merkle signature scheme," RFC 8391, May 2018. http://doi.org/10.17487/RFC8391
5. D. McGrew, M. Curcio, and S. Fluhrer, "Leighton-Micali hash-based signatures," RFC 8554, Apr. 2019. http://doi.org/10.17487/RFC8554
6. D. J. Bernstein, D. Hopwood, A. Hülsing, T. Lange, R. Niederhagen, L. Papachristodoulou, M. Schneider, P. Schwabe, and Z. Wilcox-O'Hearn, "SPHINCS: Practical stateless hash-based signatures," in Proc. of EUROCRYPT 2015, Lecture Notes in Computer Science, vol. 9056, pp. 368-397, 2015. http://doi.org/10.1007/978-3-662-46800-5_15
7. D. J. Bernstein, A. Hülsing, S. Kölbl, R. Niederhagen, J. Rijneveld, and P. Schwabe, "The SPHINCS+ signature framework," in Proc. of ACM CCS 2019, London, UK, pp. 2129-2146, 2019. http://doi.org/10.1145/3319535.3363229
8. A. Hülsing and M. Kudinov, "Recovering the tight security proof of SPHINCS+," in Proc. of ASIACRYPT 2022, Lecture Notes in Computer Science, vol. 13794, pp. 3-33, 2022. http://doi.org/10.1007/978-3-031-22972-5_1
9. M. Barbosa, F. Dupressoir, B. Grégoire, A. Hülsing, M. Meijers, and P.-Y. Strub, "Machine-checked security for XMSS as in RFC 8391 and SPHINCS+," in Proc. of CRYPTO 2023, Lecture Notes in Computer Science, vol. 14085, pp. 421-454, 2023. http://doi.org/10.1007/978-3-031-38554-4_14
10. M. Barbosa, F. Dupressoir, A. Hülsing, M. Meijers, and P.-Y. Strub, "A tight security proof for SPHINCS+, formally verified," in Proc. of ASIACRYPT 2024, Lecture Notes in Computer Science, vol. 15487, pp. 35-67, 2024. https://doi.org/10.1007/978-981-96-0894-2_2
11. A. Hülsing, M. Kudinov, E. Ronen, and E. Yogev, "SPHINCS+C: Compressing SPHINCS+ with (almost) no cost," in Proc. of 2023 IEEE Symposium on Security and Privacy, San Francisco, CA, USA, pp. 1435-1453, 2023. http://doi.org/10.1109/SP46215.2023.10179381
12. K. Zhang, H. Cui, and Y. Yu, "Revisiting the constant-sum Winternitz one-time signature with applications to SPHINCS+ and XMSS," in Proc. of CRYPTO 2023, Lecture Notes in Computer Science, vol. 14085, pp. 455-483, 2023. https://doi.org/10.1007/978-3-031-38554-4_15
13. D. Khovratovich, M. Kudinov, and B. Wagner, "At the top of the hypercube - better size-time tradeoffs for hash-based signatures," in Proc. of CRYPTO 2025, Lecture Notes in Computer Science, vol. 16005, pp. 93-123, 2025. http://doi.org/10.1007/978-3-032-01887-8_4
14. J. Mateos, "WOTS-Tree: Merkle-optimized Winternitz signatures for post-quantum Bitcoin," Cryptology ePrint Archive, Paper 2026/374, 2026. [Online]. Available: https://eprint.iacr.org/2026/374.
15. J.-P. Aumasson and G. Endignoux, "Clarifying the subset-resilience problem," Cryptology ePrint Archive, Paper 2017/909, 2017. [Online]. Available: https://eprint.iacr.org/2017/909.
16. J.-P. Aumasson and G. Endignoux, "Improving stateless hash-based signatures," in Proc. of CT-RSA 2018, Lecture Notes in Computer Science, vol. 10808, pp. 219-242, 2018. http://doi.org/10.1007/978-3-319-76953-0_12
17. M. Abri and J. Katz, "Shorter hash-based signatures using forced pruning," in Proc. of CRYPTO 2026, Lecture Notes in Computer Science, vol. 16803, pp. 573-602, 2026. https://doi.org/10.1007/978-3-032-35398-6_19
18. C. Ren, K. Zhang, and H. Yu, "Shorter hash-based signatures via bucket thinning," Cryptology ePrint Archive, Paper 2026/1328, 2026. [Online]. Available: https://eprint.iacr.org/2026/1328.
19. L. Wang, Q. Liu, H. Cui, Y. Hu, and Y. Yu, "Shorter few-time signatures from hash chains and blockwise forced pruning," Cryptology ePrint Archive, Paper 2026/2374, 2026. [Online]. Available: https://eprint.iacr.org/2026/2374.
20. C. Ren and H. Yu, "Shorter hash-based signatures via guarded sharing in a DAG model," Cryptology ePrint Archive, Paper 2026/2502, 2026. [Online]. Available: https://eprint.iacr.org/2026/2502.
21. C. Ren, K. Zhang, H. Cui, and H. Yu, "Prepared episodes for short online hash based signatures," Cryptology ePrint Archive, Paper 2026/1708, 2026. [Online]. Available: https://eprint.iacr.org/2026/1708.
22. A. Hülsing, L. Rausch, and J. Buchmann, "Optimal parameters for XMSSMT," Cryptology ePrint Archive, Paper 2017/966, 2017. [Online]. Available: https://eprint.iacr.org/2017/966.
23. S. Kölbl and J. Philipoom, "A note on SPHINCS+ parameter sets," Cryptology ePrint Archive, Paper 2022/1725, 2022. [Online]. Available: https://eprint.iacr.org/2022/1725.
24. S. Fluhrer and Q. Dang, "Smaller Sphincs+," Cryptology ePrint Archive, Paper 2024/018, 2024. [Online]. Available: https://eprint.iacr.org/2024/018.
25. Q. Dang, "Smaller SLH-DSA," NIST presentation, Sep. 2025. [Online]. Available: https://csrc.nist.gov/csrc/media/presentations/2025/sphincs-smaller-parameter-sets/sphincs-dang_2.2.pdf, Accessed on: Nov. 18, 2026.
26. Z. Qin, S. Sun, and F. Zheng, "Extending the SPHINCS+ framework: Varying the tree heights and chain lengths," in Proc. of ASIACRYPT 2026, 2026. Full version: Cryptology ePrint Archive, Paper 2025/2236. [Online]. Available: https://eprint.iacr.org/2025/2236.
27. M. Kudinov and J. Nick, "Hash-based signature schemes for Bitcoin," Cryptology ePrint Archive, Paper 2025/2203, 2025. [Online]. Available: https://eprint.iacr.org/2025/2203.
28. K. Chalkias, J. Brown, M. Hearn, T. Lillehagen, I. Nitto, and T. Schroeter, "Blockchained post-quantum signatures," in Proc. of IEEE iThings/GreenCom/CPSCom/SmartData, Halifax, NS, Canada, pp. 1196-1203, 2018. https://doi.org/10.1109/Cybermatics_2018.2018.00213
29. M. D. Noel, O. V. Waziri, M. S. Abdulhamid, and A. J. Ojeniyi, "Stateful hash-based digital signature schemes for Bitcoin cryptocurrency," in Proc. of 15th International Conference on Electronics, Computer and Computation (ICECCO), Abuja, Nigeria, pp. 1-6, 2019. https://doi.org/10.1109/ICECCO48375.2019.9043192
30. J. Nick, "SHRINCS: 324-byte stateful post-quantum signatures with static backups," Delving Bitcoin, Dec. 2025. [Online]. Available: https://delvingbitcoin.org/t/shrincs-324-byte-stateful-post-quantum-signatures-with-static-backups/2158, Accessed on: Nov. 18, 2026.
31. conduition, "SHRINCS: An efficient hash-based signature scheme for Bitcoin (first draft)," bitcoin-dev mailing list, Aug. 2026. [Online]. Available: https://groups.google.com/g/bitcoindev/c/HbVboXIFiG8, Accessed on: Nov. 18, 2026.
32. J. Nick, "SHRIMPS: 2.5 KB post-quantum signatures across multiple stateful devices," Delving Bitcoin, Mar. 2026. [Online]. Available: https://delvingbitcoin.org/t/shrimps-2-5-kb-post-quantum-signatures-across-multiple-stateful-devices/2355, Accessed on: Nov. 18, 2026.
33. Blockstream Research, "Searching for SHRINCS parameters," Aug. 2026. [Online]. Available: https://blog.blockstream.com/searching-for-shrincs-parameters/, Accessed on: Nov. 18, 2026. Model code: https://github.com/BlockstreamResearch/SPHINCS-Parameters, commit 3172178.
34. J. Nick, "OP_CHECKSHRINCS: A hash-based signature opcode for post-quantum Bitcoin," Blockstream Blog, May 2026. [Online]. Available: https://blog.blockstream.com/op_checkshrincs-a-hash-based-signature-opcode-for-post-quantum-bitcoin/, Accessed on: Nov. 18, 2026.
35. H. Beast, E. Heilman, and I. Foxen Duke, "BIP 360: Pay-to-Merkle-Root (P2MR)," Bitcoin Improvement Proposal, draft, 2026. [Online]. Available: https://bip360.org/bip360.html, Accessed on: Nov. 18, 2026.
36. R. Kysil, I. A. Seres, P. Kutas, and N. Kelecsényi, "poqeth: Efficient, post-quantum signature verification on Ethereum," in Proc. of ACM Asia Conference on Computer and Communications Security (ASIA CCS '25), Hanoi, Vietnam, pp. 327-343, Aug. 2025. https://doi.org/10.1145/3708821.3736193
37. nicocsgy, "SPHINCS minus: Efficient stateless post-quantum signature verification on the EVM," Ethereum Research forum, Jun. 2026. [Online]. Available: https://ethresear.ch/t/sphincs-minus-efficient-stateless-post-quantum-signature-verification-on-the-evm/25165, Accessed on: Nov. 18, 2026.
38. mvicari, "Achieving quantum safety through ephemeral key pairs and account abstraction," Ethereum Research forum, Mar. 2026. [Online]. Available: https://ethresear.ch/t/achieving-quantum-safety-through-ephemeral-key-pairs-and-account-abstraction/24273, Accessed on: Nov. 18, 2026.
39. opuslux, "WOTS-39: Winternitz one-time signature wallet for Ethereum," Ethereum Magicians forum, Jun. 2026. [Online]. Available: https://ethereum-magicians.org/t/post-quantum-erc-4337-wots-39-winternitz-one-time-signature-wallet-for-ethereum/28715, Accessed on: Nov. 18, 2026.
40. Ethereum Foundation Post-Quantum Team, "Post-quantum Ethereum," 2026. [Online]. Available: https://pq.ethereum.org/, Accessed on: Nov. 18, 2026.
41. M. Lie and B. Marsh, "Domain specific post quantum signatures for blockchains," arXiv:2609.24689, 2026. [Online]. Available: https://arxiv.org/abs/2609.24689.
42. J. Drake, D. Khovratovich, M. Kudinov, and B. Wagner, "Hash-based multi-signatures for post-quantum Ethereum," IACR Communications in Cryptology, vol. 2, no. 1, 2025. http://doi.org/10.62056/aey7qjp10
43. J. Drake, D. Khovratovich, M. Kudinov, and B. Wagner, "Technical note: LeanSig for post-quantum Ethereum," Cryptology ePrint Archive, Paper 2025/1332, 2025. [Online]. Available: https://eprint.iacr.org/2025/1332.
44. J. Kelsey, N. Lang, and S. Lucks, "Turning hash-based signatures into distributed signatures and threshold signatures," IACR Communications in Cryptology, vol. 2, no. 2, 2025. http://doi.org/10.62056/a6ksudy6b
45. D. Boneh, B. Bünz, J. D., Y. Litchev, and K. Nazirkhanova, "PRAWNS: Threshold hash-based signatures from threshold PRFs," Cryptology ePrint Archive, Paper 2026/2142, 2026. [Online]. Available: https://eprint.iacr.org/2026/2142.
46. T. Wiggers, K. Bashiri, S. Kölbl, J. Goodman, and S. Kousidis, "Hash-based signatures: State and backup management," RFC 10033, Sep. 2026. https://doi.org/10.17487/RFC10033
