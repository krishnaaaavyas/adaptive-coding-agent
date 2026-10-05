# STEP 8K-B.1G1E — Open-weight model landscape closure

Independent pre-outcome, candidate-blind audit. Evidence cutoff: **2026-10-03, Asia/Calcutta**. Historical project state: supplied 1G1D. No roster or protocol freeze.

## 1. Verdict

**The two Qwen checkpoints are non-redundant, but a Qwen-only primary adaptation roster leaves obvious dense, MLA, and Mamba adaptation mechanisms untested.** Recommend three additional static work items: a full Devstral Small 2 preflight, a targeted GLM-4.7-Flash preflight, and a targeted Nemotron 3.5 Lightning BF16 preflight. These are investigations that can change the roster, not admissions.

The census covers 36 exact checkpoint identities in 13 publisher families. It includes contemporary heads, significant architecture/resource transitions, and older obtainable alternatives where they establish an otherwise missing engineering path. It does not select a coding-quality winner. The current Qwen infrastructure order remains 30B first, Next second. The gpt-oss-20b proposed final-only Harmony path remains **DROP — CURRENT PROTOCOL INCOMPATIBLE**, without reopening that decision.

**STOP MODEL SHOPPING: conditional YES after the bounded work queue in section 15 resolves the three gaps or documents a source-based failure.** This closes the broad census, not every distinct architecture interaction. Known optional survivors remain visible. If an unresolved survivor demonstrates a distinct *feasible fresh-base adaptation* regime that the queue does not cover, closure must be withheld for that named gap; section 22 specifies this condition. There is no unconditional admission or unconditional closure today.

## 2. Search cutoff and methodology

Fresh public-web searches and direct official repository checks were performed on the audit date. Searches covered each required publisher, architecture and context, license files, coding-agent/SWE positioning, current self-hosted serving, and PEFT/training support. Additional scope searches included MiniMax, NVIDIA Nemotron, Google Gemma, Meta Llama, Ai2 OLMo, IBM Granite, and Microsoft Phi. Official current heads were checked against repository metadata; current Qwen 3.8, DeepSeek V4.1, GLM 5.3, Kimi K3, Nemotron 3.5, and Granite 4.2 were included rather than assuming older remembered releases were current. OLMo 3.1 and Phi-4-reasoning-plus were checked separately from older representatives.

The cutoff is the requested calendar date, not a claim to know future releases later that day. Repository creation/modification timestamps are recorded as such; they are not substituted for official announcement dates. Exact model SHA identities were resolved through public Hub metadata; small files were fetched at that SHA. GitHub support files were similarly commit-pinned. Live documentation is timestamped and byte-hashed where archived. Search-index recency was used for discovery, not to override the direct snapshot.

Only public metadata, model cards, configs, templates, licenses, and selected upstream implementation/recipe text were acquired, with a 2,000,000-byte limit per direct response. No tokenizer vocabulary or weight body was downloaded. Weight sizes and LFS identities are publisher metadata declarations, not body-hash verification. Manual-gated access was not accepted or bypassed. Fetched source was read as text and never imported/executed.

Eligibility, I, A, and P were evaluated separately. I PASS retains the supplied historical static state for the two Qwens; it does not mean an infrastructure test passed. A PASS means a technically credible fresh-original-base PEFT route is documented or supported by explicit trainable projections and compatible adapter lifecycle; it does not mean an adapter was instantiated. I/A UNCERTAIN names the missing fact. P FAIL means qualifying evidence was not established in the inspected authoritative release/model documentation; it is not a universal claim that the model cannot do SWE.

Public benchmark evaluation **existence** was recorded only for P. No performance magnitude is present in decision fields, and no such number affected inclusion, exclusion, redundancy, the work queue, or tiebreak. Unfiltered public source snapshots may contain benchmark tables, but the audit does not extract or compare their values. No project task, result, output, candidate inventory, convention, evaluator, or scorer was consulted. Secondary search results supplied discovery leads only; decisions use primary evidence. Hardware regime descriptions are engineering estimates, not a purchased topology, a fixed ceiling, or a quality ordering.

## 3. Primary sources consulted

| Exact repository/card | Immutable checkpoint SHA | Architecture/context | Terms |
| --- | --- | --- | --- |
| [Qwen3-Coder-30B-A3B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/README.md) | `b2cff646eb4bb1d68355c01b18ae02e7cf42d120` | [config](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/config.json) | [license evidence](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/LICENSE) |
| [Qwen3-Coder-Next](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/README.md) | `a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb` | [config](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/config.json) | [license evidence](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/README.md) |
| [Qwen3-Coder-480B-A35B-Instruct](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct/blob/9d90cf8fca1bf7b7acca42d3fc9ae694a2194069/README.md) | `9d90cf8fca1bf7b7acca42d3fc9ae694a2194069` | [config](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct/blob/9d90cf8fca1bf7b7acca42d3fc9ae694a2194069/config.json) | [license evidence](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct/blob/9d90cf8fca1bf7b7acca42d3fc9ae694a2194069/LICENSE) |
| [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B/blob/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0/README.md) | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` | [config](https://huggingface.co/Qwen/Qwen3.8-27B/blob/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0/config.json) | [license evidence](https://huggingface.co/Qwen/Qwen3.8-27B/blob/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0/LICENSE) |
| [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/de4b8e4d43b917e7706784d8bb445c9af86a3540/README.md) | `de4b8e4d43b917e7706784d8bb445c9af86a3540` | [config](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/de4b8e4d43b917e7706784d8bb445c9af86a3540/config.json) | [license evidence](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/de4b8e4d43b917e7706784d8bb445c9af86a3540/LICENSE) |
| [Devstral-Small-2-24B-Instruct-2512](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/README.md) | `55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128` | [config](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/config.json) | [license evidence](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/README.md) |
| [Devstral-Small-2507](https://huggingface.co/mistralai/Devstral-Small-2507/blob/bd165ab26cebbcc2eea2c4ecbfc07f3ac42b3c39/README.md) | `bd165ab26cebbcc2eea2c4ecbfc07f3ac42b3c39` | [config](https://huggingface.co/mistralai/Devstral-Small-2507/blob/bd165ab26cebbcc2eea2c4ecbfc07f3ac42b3c39/config.json) | [license evidence](https://huggingface.co/mistralai/Devstral-Small-2507/blob/bd165ab26cebbcc2eea2c4ecbfc07f3ac42b3c39/README.md) |
| [Devstral-2-123B-Instruct-2512](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512/blob/1613bf01adb5e1c6fdc196b46e6b173eae75eb4a/README.md) | `1613bf01adb5e1c6fdc196b46e6b173eae75eb4a` | [config](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512/blob/1613bf01adb5e1c6fdc196b46e6b173eae75eb4a/config.json) | [license evidence](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512/blob/1613bf01adb5e1c6fdc196b46e6b173eae75eb4a/LICENSE) |
| [gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/README.md) | `6cee5e81ee83917806bbde320786a8fb61efebee` | [config](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/config.json) | [license evidence](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/LICENSE) |
| [gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b/blob/b5c939de8f754692c1647ca79fbf85e8c1e70f8a/README.md) | `b5c939de8f754692c1647ca79fbf85e8c1e70f8a` | [config](https://huggingface.co/openai/gpt-oss-120b/blob/b5c939de8f754692c1647ca79fbf85e8c1e70f8a/config.json) | [license evidence](https://huggingface.co/openai/gpt-oss-120b/blob/b5c939de8f754692c1647ca79fbf85e8c1e70f8a/LICENSE) |
| [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/2cba9e42aa026125f3ed06c6d98c1db82f7ca027/README.md) | `2cba9e42aa026125f3ed06c6d98c1db82f7ca027` | [config](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/2cba9e42aa026125f3ed06c6d98c1db82f7ca027/config.json) | [license evidence](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/2cba9e42aa026125f3ed06c6d98c1db82f7ca027/LICENSE) |
| [DeepSeek-V4-Flash-0731](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/7872f01b1d1fe23eabc4c98b48bffcef5a386062/README.md) | `7872f01b1d1fe23eabc4c98b48bffcef5a386062` | [config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/7872f01b1d1fe23eabc4c98b48bffcef5a386062/config.json) | [license evidence](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/7872f01b1d1fe23eabc4c98b48bffcef5a386062/LICENSE) |
| [DeepSeek-V3.2](https://huggingface.co/deepseek-ai/DeepSeek-V3.2/blob/a7e62ac04ecb2c0a54d736dc46601c5606cf10a6/README.md) | `a7e62ac04ecb2c0a54d736dc46601c5606cf10a6` | [config](https://huggingface.co/deepseek-ai/DeepSeek-V3.2/blob/a7e62ac04ecb2c0a54d736dc46601c5606cf10a6/config.json) | [license evidence](https://huggingface.co/deepseek-ai/DeepSeek-V3.2/blob/a7e62ac04ecb2c0a54d736dc46601c5606cf10a6/LICENSE) |
| [DeepSeek-Coder-V2-Lite-Instruct](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct/blob/e434a23f91ba5b4923cf6c9d9a238eb4a08e3a11/README.md) | `e434a23f91ba5b4923cf6c9d9a238eb4a08e3a11` | [config](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct/blob/e434a23f91ba5b4923cf6c9d9a238eb4a08e3a11/config.json) | [license evidence](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/a2b4e0a25b5dab1ee87e8080f76e4512b0725b7b/LICENSE-MODEL) |
| [GLM-4.7-Flash](https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/README.md) | `7dd20894a642a0aa287e9827cb1a1f7f91386b67` | [config](https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/config.json) | [license evidence](https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/README.md) |
| [GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash/blob/eb9eb208eb0d988989d07a6a12d0fdeb5f52574a/README.md) | `eb9eb208eb0d988989d07a6a12d0fdeb5f52574a` | [config](https://huggingface.co/zai-org/GLM-5.3-Flash/blob/eb9eb208eb0d988989d07a6a12d0fdeb5f52574a/config.json) | [license evidence](https://huggingface.co/zai-org/GLM-5.3-Flash/blob/eb9eb208eb0d988989d07a6a12d0fdeb5f52574a/LICENSE) |
| [GLM-5.3](https://huggingface.co/zai-org/GLM-5.3/blob/aca966e4e02791568aa6a4ced368624b3d897f42/README.md) | `aca966e4e02791568aa6a4ced368624b3d897f42` | [config](https://huggingface.co/zai-org/GLM-5.3/blob/aca966e4e02791568aa6a4ced368624b3d897f42/config.json) | [license evidence](https://huggingface.co/zai-org/GLM-5.3/blob/aca966e4e02791568aa6a4ced368624b3d897f42/LICENSE) |
| [Kimi-K3](https://huggingface.co/moonshotai/Kimi-K3/blob/f831ab66814297da540d832a5235f8e904f29d06/README.md) | `f831ab66814297da540d832a5235f8e904f29d06` | [config](https://huggingface.co/moonshotai/Kimi-K3/blob/f831ab66814297da540d832a5235f8e904f29d06/config.json) | [license evidence](https://huggingface.co/moonshotai/Kimi-K3/blob/f831ab66814297da540d832a5235f8e904f29d06/LICENSE) |
| [Kimi-K2.7-Code](https://huggingface.co/moonshotai/Kimi-K2.7-Code/blob/74797c9c62378b951a1f6fcf5c4631024e9b8bef/README.md) | `74797c9c62378b951a1f6fcf5c4631024e9b8bef` | [config](https://huggingface.co/moonshotai/Kimi-K2.7-Code/blob/74797c9c62378b951a1f6fcf5c4631024e9b8bef/config.json) | [license evidence](https://huggingface.co/moonshotai/Kimi-K2.7-Code/blob/74797c9c62378b951a1f6fcf5c4631024e9b8bef/LICENSE) |
| [Kimi-Linear-48B-A3B-Instruct](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Instruct/blob/e1df551a447157d4658b573f9a695d57658590e9/README.md) | `e1df551a447157d4658b573f9a695d57658590e9` | [config](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Instruct/blob/e1df551a447157d4658b573f9a695d57658590e9/config.json) | [license evidence](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Instruct/blob/e1df551a447157d4658b573f9a695d57658590e9/README.md) |
| [Kimi-Dev-72B](https://huggingface.co/moonshotai/Kimi-Dev-72B/blob/8791d7981945752a51f692d66f2bbfb3573c9722/README.md) | `8791d7981945752a51f692d66f2bbfb3573c9722` | [config](https://huggingface.co/moonshotai/Kimi-Dev-72B/blob/8791d7981945752a51f692d66f2bbfb3573c9722/config.json) | [license evidence](https://huggingface.co/moonshotai/Kimi-Dev-72B/blob/8791d7981945752a51f692d66f2bbfb3573c9722/LICENSE.md) |
| [MiniMax-M3](https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/f0e1c1e04d40177e4673a22097036854f536e9c0/README.md) | `f0e1c1e04d40177e4673a22097036854f536e9c0` | [config](https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/f0e1c1e04d40177e4673a22097036854f536e9c0/config.json) | [license evidence](https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/f0e1c1e04d40177e4673a22097036854f536e9c0/LICENSE) |
| [MiniMax-M2.7](https://huggingface.co/MiniMaxAI/MiniMax-M2.7/blob/d494266a4affc0d2995ba1fa35c8481cbd84294b/README.md) | `d494266a4affc0d2995ba1fa35c8481cbd84294b` | [config](https://huggingface.co/MiniMaxAI/MiniMax-M2.7/blob/d494266a4affc0d2995ba1fa35c8481cbd84294b/config.json) | [license evidence](https://huggingface.co/MiniMaxAI/MiniMax-M2.7/blob/d494266a4affc0d2995ba1fa35c8481cbd84294b/LICENSE) |
| [NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/README.md) | `a9904d24bcc1d289a1950fa9d2b978c47cf903b9` | [config](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/config.json) | [license evidence](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/LICENSE) |
| [NVIDIA-Nemotron-3-Super-120B-A12B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16/blob/2dc98e2afe4face0e4ce40972a915c45368bd34a/README.md) | `2dc98e2afe4face0e4ce40972a915c45368bd34a` | [config](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16/blob/2dc98e2afe4face0e4ce40972a915c45368bd34a/config.json) | [license evidence](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16/blob/2dc98e2afe4face0e4ce40972a915c45368bd34a/README.md) |
| [NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16/blob/77df655d5e9f8362164ed14dd8b48f8bce657498/README.md) | `77df655d5e9f8362164ed14dd8b48f8bce657498` | [config](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16/blob/77df655d5e9f8362164ed14dd8b48f8bce657498/config.json) | [license evidence](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16/blob/77df655d5e9f8362164ed14dd8b48f8bce657498/README.md) |
| [gemma-4-31B-it](https://huggingface.co/google/gemma-4-31B-it/blob/842da3794eaa0b77d5f08bae87a17459d91ff475/README.md) | `842da3794eaa0b77d5f08bae87a17459d91ff475` | [config](https://huggingface.co/google/gemma-4-31B-it/blob/842da3794eaa0b77d5f08bae87a17459d91ff475/config.json) | [license evidence](https://huggingface.co/google/gemma-4-31B-it/blob/842da3794eaa0b77d5f08bae87a17459d91ff475/README.md) |
| [gemma-4-26B-A4B-it](https://huggingface.co/google/gemma-4-26B-A4B-it/blob/4d7ae4984b7db7de8f8457170b3f1a419ee76d52/README.md) | `4d7ae4984b7db7de8f8457170b3f1a419ee76d52` | [config](https://huggingface.co/google/gemma-4-26B-A4B-it/blob/4d7ae4984b7db7de8f8457170b3f1a419ee76d52/config.json) | [license evidence](https://huggingface.co/google/gemma-4-26B-A4B-it/blob/4d7ae4984b7db7de8f8457170b3f1a419ee76d52/README.md) |
| [Llama-4-Scout-17B-16E-Instruct](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct/blob/92f3b1597a195b523d8d9e5700e57e4fbb8f20d3/README.md) | `92f3b1597a195b523d8d9e5700e57e4fbb8f20d3` | config not retrieved | [license evidence](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct/blob/92f3b1597a195b523d8d9e5700e57e4fbb8f20d3/LICENSE) |
| [Olmo-3-32B-Think](https://huggingface.co/allenai/Olmo-3-32B-Think/blob/f2edda15216e738ef2bb73771e11890e152b2112/README.md) | `f2edda15216e738ef2bb73771e11890e152b2112` | [config](https://huggingface.co/allenai/Olmo-3-32B-Think/blob/f2edda15216e738ef2bb73771e11890e152b2112/config.json) | [license evidence](https://huggingface.co/allenai/Olmo-3-32B-Think/blob/f2edda15216e738ef2bb73771e11890e152b2112/README.md) |
| [MiniMax-M2.5](https://huggingface.co/MiniMaxAI/MiniMax-M2.5/blob/f710177d938eff80b684d42c5aa84b382612f21f/README.md) | `f710177d938eff80b684d42c5aa84b382612f21f` | [config](https://huggingface.co/MiniMaxAI/MiniMax-M2.5/blob/f710177d938eff80b684d42c5aa84b382612f21f/config.json) | [license evidence](https://huggingface.co/MiniMaxAI/MiniMax-M2.5/blob/f710177d938eff80b684d42c5aa84b382612f21f/LICENSE-MODEL) |
| [granite-4.1-30b](https://huggingface.co/ibm-granite/granite-4.1-30b/blob/4fae6278f7132abf5e971f9de49ebbad09c54cce/README.md) | `4fae6278f7132abf5e971f9de49ebbad09c54cce` | [config](https://huggingface.co/ibm-granite/granite-4.1-30b/blob/4fae6278f7132abf5e971f9de49ebbad09c54cce/config.json) | [license evidence](https://huggingface.co/ibm-granite/granite-4.1-30b/blob/4fae6278f7132abf5e971f9de49ebbad09c54cce/README.md) |
| [phi-4](https://huggingface.co/microsoft/phi-4/blob/2db69c1c3e91a05d2c64a3185acfbaf36f744e25/README.md) | `2db69c1c3e91a05d2c64a3185acfbaf36f744e25` | [config](https://huggingface.co/microsoft/phi-4/blob/2db69c1c3e91a05d2c64a3185acfbaf36f744e25/config.json) | [license evidence](https://huggingface.co/microsoft/phi-4/blob/2db69c1c3e91a05d2c64a3185acfbaf36f744e25/LICENSE) |
| [granite-4.2-8b](https://huggingface.co/ibm-granite/granite-4.2-8b/blob/f8de16cdcdbc6c779ca517604e050d82cc119e44/README.md) | `f8de16cdcdbc6c779ca517604e050d82cc119e44` | [config](https://huggingface.co/ibm-granite/granite-4.2-8b/blob/f8de16cdcdbc6c779ca517604e050d82cc119e44/config.json) | [license evidence](https://huggingface.co/ibm-granite/granite-4.2-8b/blob/f8de16cdcdbc6c779ca517604e050d82cc119e44/README.md) |
| [Olmo-3.1-32B-Instruct](https://huggingface.co/allenai/Olmo-3.1-32B-Instruct/blob/ac0587e4a7744a551c059d8cd17ba220bc940dae/README.md) | `ac0587e4a7744a551c059d8cd17ba220bc940dae` | [config](https://huggingface.co/allenai/Olmo-3.1-32B-Instruct/blob/ac0587e4a7744a551c059d8cd17ba220bc940dae/config.json) | [license evidence](https://huggingface.co/allenai/Olmo-3.1-32B-Instruct/blob/ac0587e4a7744a551c059d8cd17ba220bc940dae/README.md) |
| [Phi-4-reasoning-plus](https://huggingface.co/microsoft/Phi-4-reasoning-plus/blob/69baf8528e1bcf05f475034d9e5dd32875ed125f/README.md) | `69baf8528e1bcf05f475034d9e5dd32875ed125f` | [config](https://huggingface.co/microsoft/Phi-4-reasoning-plus/blob/69baf8528e1bcf05f475034d9e5dd32875ed125f/config.json) | [license evidence](https://huggingface.co/microsoft/Phi-4-reasoning-plus/blob/69baf8528e1bcf05f475034d9e5dd32875ed125f/LICENSE) |

All 36 Hub metadata responses and retrieved model text files are inventoried with URLs, bytes, SHA-256, status, and server retrieval dates in `source_manifest.json`. Every decision can be joined to its repository and exact revision in `landscape.csv`. A SHA identifies the published checkpoint tree; it does not certify every weight body has been obtained.

Additional primary implementation and adaptation sources:
| Repository | Pinned support revision | Evidence read |
| --- | --- | --- |
| huggingface/transformers | `02d8fb9784e8f14a1251e4c992cd82a5762417c6` | modeling_glm4_moe_lite.py; modeling_nemotron_h.py; modeling_mistral3.py; modeling_ministral3.py; modeling_gemma4.py; modeling_qwen3_5.py; quantizer_finegrained_fp8.py |
| huggingface/peft | `532a05dd505c28993119b7715ee286f4234bf51b` | config.py; peft_model.py; model.py |
| hiyouga/LlamaFactory | `ce9dc9e072f80fa3abe0989d4ab90da25f083438` | README.md |
| NVIDIA-NeMo/Nemotron | `8749344f8ccefd50181c56b013ddc5c8a6154a8c` | README.md; lora.md; README.md; sft.md |
| NVIDIA-NeMo/Megatron-Bridge | `721356847b79c4bf78e5b8e9ceb6ed87835d3872` | README.md; nemotron3.5-lightning.md |
| vllm-project/recipes | `cbf76c0dedcd4404e2ca6a6ac14f00bbf4215888` | Qwen3.8-Flash-Next.yaml |
| vllm-project/vllm | `5f30fc7031cae49bf51073fc953d419b08f8887c` | supported_models.md; lora.md; glm4_moe_lite.py |
| MoonshotAI/Kimi-Dev | `5f60757f5ef54f66455c209aca169c8f850b96bd` | README.md; LICENSE.md |
| deepseek-ai/DeepSeek-Coder-V2 | `a2b4e0a25b5dab1ee87e8080f76e4512b0725b7b` | README.md; LICENSE-MODEL |

Official live sources include the [Mistral release](https://mistral.ai/news/devstral-2-vibe-cli), [Google Gemma license page](https://ai.google.dev/gemma/docs/gemma_4_license), [Hugging Face/Google Gemma release guide](https://huggingface.co/blog/gemma4), [OpenAI model card, section 2.6](https://deploymentsafety.openai.com/gpt-oss), [NVIDIA distributed Super adaptation guide](https://docs.nvidia.com/nemotron/latest/nemotron/super3/sft.html), [PEFT v0.21 LoRA parameter documentation](https://huggingface.co/docs/peft/v0.21.0/package_reference/lora), [DeepSeek V3.2 author report, section 4.1](https://arxiv.org/html/2512.02556v1#S4.SS1), and [NVIDIA Ultra author report, Table 10](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf). Web-only consultation records distinguish unarchived bytes from archived sources. Failed guessed documentation paths remain marked unavailable; they are not represented as inspected evidence.

## 4. Landscape census

| Family | Checkpoint scope | Why investigated / grouping limit |
| --- | --- | --- |
| Qwen | Coder 30B, Next, 480B; 3.8 dense 27B and Flash Next | Full-attention MoE, DeltaNet MoE, dense recurrence, and new QSA/conditional-memory architecture. API Qwen3.8-Flash is not silently equated to the obtainable Flash-Next checkpoint. |
| Mistral/Devstral | Small 2 24B 2512; Small 2507 BF16; 123B 2512 | SWE-specific dense family, Tekken serialization, native FP8 versus BF16, Apache versus revenue-conditioned modified MIT. |
| OpenAI | gpt-oss 20b and 120b | Harmony and native MXFP4 experts; historical final-only projection remains closed. |
| DeepSeek | V4.1 Flash; V4 Flash 0731; V3.2; Coder V2 Lite Instruct | Current CSA/Engram/mHC heads, DSA/MLA lineage, and a small BF16 MLA alternative. Not every legacy V3/R1 post-training variant is enumerated. |
| Z.ai | GLM 4.7 Flash; 5.3 Flash; 5.3 | Small MLA and new sparse/linear/mHC versus large DSA; do not inherit older MIT terms to the large 5.3 head. |
| Moonshot | Kimi K3; K2.7 Code; Linear 48B; Dev 72B | KDA/latent expert head, K2 MLA coding checkpoint, experimental KDA+MLA, and Qwen2-derived dense SWE model. K2.5/2.6 are documented ancestors, not silently classified redundant. |
| MiniMax | M3; M2.7; M2.5 | Sparse-attention head and M2 full-attention line; explicit terms differ across releases. |
| NVIDIA | Nemotron Lightning 3.5 30B, Super 120B, Ultra 550B BF16 | Mamba2+MoE, latent expert transitions, explicit custom-kernel adaptation recipes, and three residency regimes. FP8/NVFP4 siblings are packaging alternatives, not extra subjects here. |
| Google | Gemma4 dense 31B and MoE 26B-A4B | Native channel serialization and dense/expert BF16; official collaborative release guide establishes coding-agent positioning. Smaller 12B/E variants remain family scope, not a claim of identical regime. |
| Meta | Llama4 Scout 17B-16E | Gated multimodal expert representative; access/terms uncertain and P unestablished. |
| Ai2 | OLMo3 Think 32B and current OLMo3.1 Instruct 32B | Fully open dense training lineage, but inspected current P documentation does not meet the mechanical SWE gate. |
| IBM | Granite4.1 30B and current Granite4.2 8B | The newer head documents SWE evaluation and coding-agent integration; do not inherit that evidence backwards. |
| Microsoft | Phi4 and Phi4-reasoning-plus | 16k versus 32k nominal context; generic coding and benchmark decontamination are insufficient P evidence. |

This is a reasonable bounded census, not a proof that every public fine-tune was found. Managed API-only systems, embeddings, specialized modality models, and community derivatives without authoritative SWE positioning are outside the search target. No family was included merely to increase vendor diversity. Distinct contemporary mechanisms are visible even when their inference/adaptation path is only a reference or remains uncertain.

## 5. Eligibility table

Five gates are shown separately: W = obtainable self-hosted weights; R = immutable checkpoint identity; L = intended research/product terms; API = core intelligence needs no proprietary API; D = enough published documentation for I/A/P. License PASS includes ordinary notice/use obligations and is scoped to the stated general SWE research/product use; undisclosed organizational/revenue/geographic facts are not invented. Terms-dependent models remain UNCERTAIN. W PASS is public artifact listing/access evidence, not a weight-download test. D PASS means the gate can be evaluated, not that it passes.

| Checkpoint | W | R | L | API | D | Overall | Material license/access evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3-Coder-30B-A3B-Instruct | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0; card and LICENSE |
| Qwen3-Coder-Next | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative card declaration; standalone LICENSE absent |
| Qwen3-Coder-480B-A35B-Instruct | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0; LICENSE |
| Qwen3.8-27B | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0; LICENSE |
| Qwen3.8-Flash-Next | PASS | PASS | UNCERTAIN | PASS | PASS | UNCERTAIN | Qwen Community 1.0: commercial Model as a Service or AI Work Assistant business requires separate license; internal-use exception |
| Devstral-Small-2-24B-Instruct-2512 | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative card and release; standalone LICENSE absent |
| Devstral-Small-2507 | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative card |
| Devstral-2-123B-Instruct-2512 | PASS | PASS | UNCERTAIN | PASS | PASS | UNCERTAIN | Modified MIT: no rights if consolidated monthly company/employer revenue exceeds USD20M absent separate license |
| gpt-oss-20b | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0; LICENSE |
| gpt-oss-120b | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0; LICENSE |
| DeepSeek-V4.1-Flash | PASS | PASS | PASS | PASS | PASS | PASS | MIT; LICENSE |
| DeepSeek-V4-Flash-0731 | PASS | PASS | PASS | PASS | PASS | PASS | MIT; LICENSE |
| DeepSeek-V3.2 | PASS | PASS | PASS | PASS | PASS | PASS | MIT; LICENSE |
| DeepSeek-Coder-V2-Lite-Instruct | PASS | PASS | PASS | PASS | PASS | PASS | DeepSeek Model License via official GitHub LICENSE-MODEL; commercial use allowed subject to use restrictions |
| GLM-4.7-Flash | PASS | PASS | PASS | PASS | PASS | PASS | MIT; LICENSE |
| GLM-5.3-Flash | PASS | PASS | PASS | PASS | PASS | PASS | MIT; LICENSE |
| GLM-5.3 | PASS | PASS | UNCERTAIN | PASS | PASS | UNCERTAIN | GLM-5.3 License: Model as a Service businesses above USD10B aggregate 12-month revenue require security review |
| Kimi-K3 | PASS | PASS | UNCERTAIN | PASS | PASS | UNCERTAIN | Kimi K3 License: Model as a Service above USD20M aggregate 12-month revenue requires agreement; internal-use exception and high-scale attribution |
| Kimi-K2.7-Code | PASS | PASS | PASS | PASS | PASS | PASS | Modified MIT: high-MAU or monthly-revenue products require visible model attribution |
| Kimi-Linear-48B-A3B-Instruct | PASS | PASS | PASS | PASS | PASS | PASS | MIT; LICENSE |
| Kimi-Dev-72B | PASS | PASS | PASS | PASS | PASS | PASS | MIT derivative license; documented Qwen2.5-72B base obligations also apply |
| MiniMax-M3 | PASS | PASS | UNCERTAIN | PASS | PASS | UNCERTAIN | MiniMax Community: commercial notice plus attribution; authorization above USD20M yearly product/service revenue |
| MiniMax-M2.7 | PASS | PASS | FAIL | PASS | PASS | FAIL | Non-commercial license; commercial use requires prior written authorization, with personal/non-commercial research exceptions |
| NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | PASS | PASS | PASS | PASS | PASS | PASS | OpenMDW-1.1; LICENSE |
| NVIDIA-Nemotron-3-Super-120B-A12B-BF16 | PASS | PASS | PASS | PASS | PASS | PASS | NVIDIA Nemotron Open Model License; linked terms retrieved, not assumed Apache |
| NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 | PASS | PASS | PASS | PASS | PASS | PASS | OpenMDW-1.1 governing terms; authoritative linked license retrieved |
| gemma-4-31B-it | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative model declaration and Google license page |
| gemma-4-26B-A4B-it | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative model declaration and Google license page |
| Llama-4-Scout-17B-16E-Instruct | UNCERTAIN | PASS | UNCERTAIN | PASS | UNCERTAIN | UNCERTAIN | Llama4 Community License: gated acceptance, use/redistribution restrictions and high-MAU licensing; applicability unresolved |
| Olmo-3-32B-Think | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative card; research/educational intent is not asserted to be a non-commercial license restriction |
| MiniMax-M2.5 | PASS | PASS | PASS | PASS | PASS | PASS | Actual LICENSE-MODEL is MiniMax Model License with use/redistribution restrictions; card Modified-MIT link does not establish its terms |
| granite-4.1-30b | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative card |
| phi-4 | PASS | PASS | PASS | PASS | PASS | PASS | MIT; LICENSE |
| granite-4.2-8b | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative card |
| Olmo-3.1-32B-Instruct | PASS | PASS | PASS | PASS | PASS | PASS | Apache-2.0 authoritative card |
| Phi-4-reasoning-plus | PASS | PASS | PASS | PASS | PASS | PASS | MIT; LICENSE |

For Llama4, ungated metadata/card/license are available but original config/tokenizer access is manual-gated; no acceptance was attempted. For MiniMax M2.7, the unqualified commercial product-development path fails; separately permitted personal/non-commercial research is not falsely described as prohibited or substituted for the user's combined scope. For Kimi Dev, the derivative MIT statement does not erase documented base obligations. M2.5's actual LICENSE-MODEL takes precedence over its card's Modified-MIT label.

## 6. I — inference-feasibility table

The required deployed budget is **at least 32,768 tokens total, including the existing 2,048-token generation reserve**. Native maximum context is evidence, not proof of usable deployed capacity. Do not add the reserve again to require 34,816, and do not grant extensions merely to rescue a failure. Greedy controls, full emitted stream, terminal token identities, replacement output capacity, tools-disabled operation, and offline/no-read isolation must all be retained.

| Checkpoint | I | Native pinned config context | Serialization / channels | Decision or unresolved fact |
| --- | --- | --- | --- | --- |
| Qwen3-Coder-30B-A3B-Instruct | PASS | 262144 | Qwen BPE / ChatML, non-thinking | Historical draft3 static path retained; actual 32768/2048 capacity, greedy controls, terminals and isolation still need infrastructure verification [config](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/config.json) |
| Qwen3-Coder-Next | PASS | 262144 | Qwen BPE / ChatML, non-thinking | Historical static path retained; hybrid recurrent-state isolation and TP determinism still unmeasured [config](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/config.json) |
| Qwen3-Coder-480B-A35B-Instruct | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | Qwen BPE / ChatML, non-thinking | Serving family supported; exact topology, capacity and terminal accounting unverified [config](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct/blob/9d90cf8fca1bf7b7acca42d3fc9ae694a2194069/config.json) |
| Qwen3.8-27B | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | New Qwen multimodal BPE / ChatML; default thinking | Native thinking-disabled prefix is documented, but its draft3 admissibility and raw emitted suffix must be established; no final-only parser [config](https://huggingface.co/Qwen/Qwen3.8-27B/blob/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0/config.json) |
| Qwen3.8-Flash-Next | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | Qwen4 experimental tokenizer/template; default thinking | QSA plus n-gram/PLE offload; pinned vLLM recipe documents TP4 startup OOM without CPU offload on 80GB devices; not the managed Qwen3.8-Flash API model [config](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/de4b8e4d43b917e7706784d8bb445c9af86a3540/config.json) |
| Devstral-Small-2-24B-Instruct-2512 | UNCERTAIN — PREFLIGHT REQUIRED | 393216 | Tekken / Mistral instructions; text-only use of multimodal checkpoint | Card advertises 256k; pinned text config says 393216; certify 32768 rather than assume either native maximum; optional tools must remain disabled [config](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/config.json) |
| Devstral-Small-2507 | UNCERTAIN — PREFLIGHT REQUIRED | 131072 | Tekken / Mistral instructions; text-only BF16 | Native 128k and self-hosting documented; exact template, greedy and terminal controls need static verification [config](https://huggingface.co/mistralai/Devstral-Small-2507/blob/bd165ab26cebbcc2eea2c4ecbfc07f3ac42b3c39/config.json) |
| Devstral-2-123B-Instruct-2512 | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | Tekken / Mistral instructions | 256k and local serving documented; exact template and quantized deployment unverified [config](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512/blob/1613bf01adb5e1c6fdc196b46e6b173eae75eb4a/config.json) |
| gpt-oss-20b | FAIL | 131072 | Harmony analysis/final serialization | Proposed final-only Harmony path remains DROP under 1G1D; no reopening, suppression, retry or budget accommodation [config](https://huggingface.co/openai/gpt-oss-20b/blob/6cee5e81ee83917806bbde320786a8fb61efebee/config.json) |
| gpt-oss-120b | FAIL | 131072 | Harmony analysis/final serialization | Same proposed final-only substantive-channel projection would violate unchanged draft3; does not infer every possible output is invalid [config](https://huggingface.co/openai/gpt-oss-120b/blob/b5c939de8f754692c1647ca79fbf85e8c1e70f8a/config.json) |
| DeepSeek-V4.1-Flash | UNCERTAIN — PREFLIGHT REQUIRED | 1048576 | DeepSeek protocol-aware encoding; thinking and tool syntax | CSA2, FP4 KV, mHC, Engram and DSpark; actual original serializer/runtime equality unresolved; tools/speculation optional in study profile [config](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/2cba9e42aa026125f3ed06c6d98c1db82f7ca027/config.json) |
| DeepSeek-V4-Flash-0731 | UNCERTAIN — PREFLIGHT REQUIRED | 1048576 | DeepSeek revised encoding / thinking / tool messages | 1M config, native sparse/compressed serving; exact 32768/2048 and native suffix need verification [config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/7872f01b1d1fe23eabc4c98b48bffcef5a386062/config.json) |
| DeepSeek-V3.2 | UNCERTAIN — PREFLIGHT REQUIRED | 163840 | DeepSeek custom encoding, thinking-with-tools | Card native maximum 128k versus config 163840; offline serving plausible, not measured; no output reasoning deletion [config](https://huggingface.co/deepseek-ai/DeepSeek-V3.2/blob/a7e62ac04ecb2c0a54d736dc46601c5606cf10a6/config.json) |
| DeepSeek-Coder-V2-Lite-Instruct | UNCERTAIN — PREFLIGHT REQUIRED | 163840 | DeepSeek V2 BPE/template; instruction checkpoint | 128k card / 163840 config; self-hosting documented, source-specific EOS and current replacement capacity unverified [config](https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct/blob/e434a23f91ba5b4923cf6c9d9a238eb4a08e3a11/config.json) |
| GLM-4.7-Flash | UNCERTAIN — PREFLIGHT REQUIRED | 202752 | GLM BPE / GLM roles; default think prefix | 202752 config, 32768 plausible; native non-thinking template closes think in INPUT, but admissibility and exact emitted suffix must be established without final extraction [config](https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/config.json) |
| GLM-5.3-Flash | UNCERTAIN — PREFLIGHT REQUIRED | 1048576 | GLM next multimodal template; default max reasoning effort | Native 1M, linear/sparse attention and mHC; exact raw stream/profile unverified [config](https://huggingface.co/zai-org/GLM-5.3-Flash/blob/eb9eb208eb0d988989d07a6a12d0fdeb5f52574a/config.json) |
| GLM-5.3 | UNCERTAIN — PREFLIGHT REQUIRED | 1048576 | GLM template; default max reasoning effort | 1M config and self-hosted recipes; cap/channel controls not verified [config](https://huggingface.co/zai-org/GLM-5.3/blob/aca966e4e02791568aa6a4ced368624b3d897f42/config.json) |
| Kimi-K3 | UNCERTAIN — PREFLIGHT REQUIRED | 1048576 | Kimi role/channel serialization; always thinking enabled | Mandatory reasoning_content documented; official final-content-only example is not a draft3 profile; full-stream alternative remains uncertified [config](https://huggingface.co/moonshotai/Kimi-K3/blob/f831ab66814297da540d832a5235f8e904f29d06/config.json) |
| Kimi-K2.7-Code | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | Kimi K2.5/K2.6 serialization and architecture reused | 256k config, self-hosting documented; output stream and terminal handling not certified [config](https://huggingface.co/moonshotai/Kimi-K2.7-Code/blob/74797c9c62378b951a1f6fcf5c4631024e9b8bef/config.json) |
| Kimi-Linear-48B-A3B-Instruct | UNCERTAIN — PREFLIGHT REQUIRED | UNVERIFIED | Kimi roles / KDA plus MLA | 1M card, custom model code and FLA; current serving documented but exact study profile unverified [config](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Instruct/blob/e1df551a447157d4658b573f9a695d57658590e9/config.json) |
| Kimi-Dev-72B | UNCERTAIN — PREFLIGHT REQUIRED | 131072 | Qwen2 BPE / ChatML | 128k, whole-model self-hosting documented; no mandatory proprietary agent; exact serializer/profile unverified [config](https://huggingface.co/moonshotai/Kimi-Dev-72B/blob/8791d7981945752a51f692d66f2bbfb3573c9722/config.json) |
| MiniMax-M3 | UNCERTAIN — PREFLIGHT REQUIRED | 1048576 | MiniMax multimodal template; enabled/adaptive/disabled reasoning modes | 1M and MSA self-hosting supported; raw stream and optional tool behavior unverified [config](https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/f0e1c1e04d40177e4673a22097036854f536e9c0/config.json) |
| MiniMax-M2.7 | UNCERTAIN — PREFLIGHT REQUIRED | 204800 | MiniMax M2 template and reasoning | 204800 context and local serving; exact raw profile not certified [config](https://huggingface.co/MiniMaxAI/MiniMax-M2.7/blob/d494266a4affc0d2995ba1fa35c8481cbd84294b/config.json) |
| NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | 131072-vocabulary tokenizer / ChatML-style; default think prefix | Card 1M extended context versus native config 262144; greedy alone does not certify cache stochastic rounding, SSM state isolation or raw boundaries [config](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/config.json) |
| NVIDIA-Nemotron-3-Super-120B-A12B-BF16 | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | Nemotron template / configurable thinking | Native config 262144; actual study profile/cache isolation unverified [config](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16/blob/2dc98e2afe4face0e4ce40972a915c45368bd34a/config.json) |
| NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | Nemotron template / reasoning | Native config 262144 and documented extended context; protocol-specific runtime unresolved [config](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16/blob/77df655d5e9f8362164ed14dd8b48f8bce657498/config.json) |
| gemma-4-31B-it | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | Gemma4 turns and thought/final channels | 262144 config; configurable thinking and channel parser require full emitted content; no Harmony analogy silently applied [config](https://huggingface.co/google/gemma-4-31B-it/blob/842da3794eaa0b77d5f08bae87a17459d91ff475/config.json) |
| gemma-4-26B-A4B-it | UNCERTAIN — PREFLIGHT REQUIRED | 262144 | Gemma4 turns and thought/final channels | 262144 config; same raw-channel and full-artifact concerns as dense Gemma4 [config](https://huggingface.co/google/gemma-4-26B-A4B-it/blob/4d7ae4984b7db7de8f8457170b3f1a419ee76d52/config.json) |
| Llama-4-Scout-17B-16E-Instruct | UNCERTAIN — PREFLIGHT REQUIRED | UNVERIFIED | Llama4 native serialization; gated tokenizer/config not retrieved | Published self-hosted weights are listed, but access and exact template/config cannot be certified from ungated metadata config not retrieved |
| Olmo-3-32B-Think | UNCERTAIN — PREFLIGHT REQUIRED | 65536 | OLMo BPE / thinking-generation template | 65536 config; default thinking and full-stream cap/terminals unverified [config](https://huggingface.co/allenai/Olmo-3-32B-Think/blob/f2edda15216e738ef2bb73771e11890e152b2112/config.json) |
| MiniMax-M2.5 | UNCERTAIN — PREFLIGHT REQUIRED | 196608 | MiniMax M2 BPE/template and reasoning | 196608 and self-hosting documented; exact output/count controls unresolved [config](https://huggingface.co/MiniMaxAI/MiniMax-M2.5/blob/f710177d938eff80b684d42c5aa84b382612f21f/config.json) |
| granite-4.1-30b | UNCERTAIN — PREFLIGHT REQUIRED | 131072 | Granite roles/template | 131072 config; exact original profile unverified [config](https://huggingface.co/ibm-granite/granite-4.1-30b/blob/4fae6278f7132abf5e971f9de49ebbad09c54cce/config.json) |
| phi-4 | FAIL | 16384 | Phi3 family tokenizer/template | Pinned config max_position_embeddings=16384, below 32768 required; no context extension accommodation [config](https://huggingface.co/microsoft/phi-4/blob/2db69c1c3e91a05d2c64a3185acfbaf36f744e25/config.json) |
| granite-4.2-8b | UNCERTAIN — PREFLIGHT REQUIRED | 131072 | Granite / ChatML-style, default thinking | 131072 native config versus extension up to 512k; custom reasoning parser is not authorized content projection; static native-mode legality needs confirmation [config](https://huggingface.co/ibm-granite/granite-4.2-8b/blob/f8de16cdcdbc6c779ca517604e050d82cc119e44/config.json) |
| Olmo-3.1-32B-Instruct | UNCERTAIN — PREFLIGHT REQUIRED | 65536 | OLMo BPE / non-thinking instruction template | 65536 config and local Transformers/vLLM support; exact deployed profile unverified [config](https://huggingface.co/allenai/Olmo-3.1-32B-Instruct/blob/ac0587e4a7744a551c059d8cd17ba220bc940dae/config.json) |
| Phi-4-reasoning-plus | UNCERTAIN — PREFLIGHT REQUIRED | 32768 | Phi3 BPE / reasoning template | 32768 config exactly meets nominal threshold; deployed usable budget remains unverified; do not inherit phi-4 16384 failure [config](https://huggingface.co/microsoft/Phi-4-reasoning-plus/blob/69baf8528e1bcf05f475034d9e5dd32875ed125f/config.json) |

For every new plausible serving path, deployed greedy/sampling precedence, max-new-tokens=2048, EOS versus tool-handoff meanings, complete replacement emission, optional tool-loop removal, external-read isolation, and process/KV/recurrent-state reset remain unverified unless a row names a specific failure. Model-card sampled-agent recipes are not imported as study generation settings. An OpenAI-compatible local endpoint is transport, not a requirement for OpenAI's commercial API.

The historical gpt-oss exclusion concerns the proposed substantive analysis-to-final projection. The 120b row applies the same rejected projection to the family reference; it does not establish that all conceivable native Harmony paths are impossible, nor initiate a new Harmony audit. Source stop strings or special-token filtering cannot be used to delete substantive output. Native input-template controls are candidate facts to adjudicate against unchanged draft3, not approval to suppress reasoning. A valid profile must preserve the entire emitted textual completion apart from the already allowed native terminal removal and CRLF/CR normalization.

## 7. A — adaptation-feasibility table

A is independent of I. Repeated adaptation must reload the exact ORIGINAL BASE each cycle, with new adapter and optimizer/scheduler/RNG state, then support saved-adapter reload and either original-base merge/export or compatible direct-adapter serving. A framework's general fine-tuning page is not an exact-checkpoint roundtrip certification. Fused expert Parameters need explicit parameter targeting or a declared attention-only scope; module names alone can miss them.

| Checkpoint | A | Credible route / unresolved facts |
| --- | --- | --- |
| Qwen3-Coder-30B-A3B-Instruct | PASS | Historical explicit attention/expert Linear LoRA; ORIGINAL BASE reset and merge lifecycle unmeasured |
| Qwen3-Coder-Next | PASS | Historical full/linear-attention and expert LoRA path; fresh base/optimizer reset and export unmeasured |
| Qwen3-Coder-480B-A35B-Instruct | PASS | Credible ordinary Qwen MoE PEFT path; roughly 960GB BF16 checkpoint makes repeated reload/merge a separate cluster operation without an evidenced project cycle plan |
| Qwen3.8-27B | UNCERTAIN — PREFLIGHT REQUIRED | Dense DeltaNet source exists; exact fused-kernel-safe targets and same-base adapter export not certified |
| Qwen3.8-Flash-Next | UNCERTAIN — PREFLIGHT REQUIRED | Gated residual, lookup tables and expert representation need model-specific differentiation/export support; active count omits 51B conditional memory and MTP |
| Devstral-Small-2-24B-Instruct-2512 | UNCERTAIN — PREFLIGHT REQUIRED | Native static FP8 is not automatically trainable: pinned Transformers FP8 quantizer reports is_trainable=False; verify deterministic dequantization of THIS original checkpoint, safe dense targets, save/reload/export |
| Devstral-Small-2507 | PASS | Dense BF16 Mistral Linears plus explicit PEFT targets offer credible fresh-base/merge path; never silently substitute it for Small 2 |
| Devstral-2-123B-Instruct-2512 | UNCERTAIN — PREFLIGHT REQUIRED | Large dense FP8 checkpoint needs supported conversion and repeated distributed base reload/export |
| gpt-oss-20b | PASS | Historical BF16 fresh-base PEFT path plausible; native MXFP4 inference fit does not establish training fit |
| gpt-oss-120b | UNCERTAIN — PREFLIGHT REQUIRED | Larger original quantized-to-training conversion and expert targets not preflighted |
| DeepSeek-V4.1-Flash | UNCERTAIN — PREFLIGHT REQUIRED | 552B backbone plus 196B Engram and specialized quantization need backward, immutable-base conversion and export support not established by inference recipes |
| DeepSeek-V4-Flash-0731 | UNCERTAIN — PREFLIGHT REQUIRED | Low-bit expert/FP8 storage and compressed attention do not prove trainable kernels or same-base roundtrip; direct LoRA not declared in inspected vLLM table |
| DeepSeek-V3.2 | UNCERTAIN — PREFLIGHT REQUIRED | Direct vLLM LoRA is declared for architecture; native FP8 training and fresh distributed BF16 conversion/merge not certified for this original checkpoint |
| DeepSeek-Coder-V2-Lite-Instruct | PASS | BF16 MLA/expert architecture and PEFT plus vLLM LoRA provide credible explicit-target path; no instantiated adapter |
| GLM-4.7-Flash | PASS | Pinned source has ordinary MLA projection Linears and 3D expert Parameters; attention-only LoRA credible, expert coverage requires target_parameters and runtime-format mapping |
| GLM-5.3-Flash | UNCERTAIN — PREFLIGHT REQUIRED | FP8 native serving plus new hybrid backward/merge and expert representation unresolved; BF16 companion is a different artifact requiring explicit provenance |
| GLM-5.3 | UNCERTAIN — PREFLIGHT REQUIRED | Native FP8-to-BF16 repeated distributed loop and DSA expert/export support require their own plan |
| Kimi-K3 | UNCERTAIN — PREFLIGHT REQUIRED | Native MXFP4, KDA, latent experts, AttnRes and massive base need explicit training/conversion/export support; blank direct-LoRA support is not proof of impossibility |
| Kimi-K2.7-Code | UNCERTAIN — PREFLIGHT REQUIRED | Native compressed-tensor quantization and roughly 1T logical model require cluster original-base reconstruction and merge/export plan; no supported repeated project route established |
| Kimi-Linear-48B-A3B-Instruct | UNCERTAIN — PREFLIGHT REQUIRED | KDA backward/custom kernels and adapter export need verification; cannot borrow Qwen DeltaNet certification |
| Kimi-Dev-72B | PASS | Ordinary Qwen2 dense targets and adapter merge path credible; 145GB BF16 base requires distributed reload planning |
| MiniMax-M3 | UNCERTAIN — PREFLIGHT REQUIRED | 428B-scale BF16 storage, sparse-attention backward and export require distributed plan; inference support alone insufficient |
| MiniMax-M2.7 | UNCERTAIN — PREFLIGHT REQUIRED | Native FP8 conversion and repeated distributed loop unresolved; M2 serving support cannot establish M2.7 license permission |
| NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | PASS | Exact NVIDIA LoRA recipe plus Megatron-Bridge original-base reload/export support; station recipe excludes Mamba out_proj because kernels consume raw weight; target coverage must be declared |
| NVIDIA-Nemotron-3-Super-120B-A12B-BF16 | PASS | Official distributed Megatron-Bridge LoRA recipe; 247GB BF16 checkpoint plus latent experts require fresh sharded reload/export plan not established in project |
| NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 | UNCERTAIN — PREFLIGHT REQUIRED | 1.12TB BF16 package; family training support exists, but exact repeated PEFT import/reset/merge/export topology remains unestablished here |
| gemma-4-31B-it | PASS | Pinned Gemma4 text projections plus release-guide PEFT support provide a credible BF16 attention-target save/reload/merge path; expert coverage for 26B and multimodal exclusions must be declared |
| gemma-4-26B-A4B-it | PASS | Pinned Gemma4 text projections plus release-guide PEFT support provide a credible BF16 attention-target save/reload/merge path; expert coverage for 26B and multimodal exclusions must be declared |
| Llama-4-Scout-17B-16E-Instruct | UNCERTAIN — PREFLIGHT REQUIRED | PEFT supports Llama4 parameter experts in principle; gated original identity/target/runtime/export unverified |
| Olmo-3-32B-Think | UNCERTAIN — PREFLIGHT REQUIRED | Dense trainable framework exists, but exact PEFT targets and same-base export not preflighted |
| MiniMax-M2.5 | UNCERTAIN — PREFLIGHT REQUIRED | Native FP8 original plus M2 serving LoRA support provide possible path, not verified fresh-base quantized training/export |
| granite-4.1-30b | UNCERTAIN — PREFLIGHT REQUIRED | Dense architecture suggests ordinary targets, but model-specific reset/export not audited |
| phi-4 | UNCERTAIN — PREFLIGHT REQUIRED | PEFT conceivable, but deeper preflight unnecessary after required gates fail |
| granite-4.2-8b | UNCERTAIN — PREFLIGHT REQUIRED | Small dense original residency is credible; explicit safe targets and fresh-base adapter serialization/export require check |
| Olmo-3.1-32B-Instruct | UNCERTAIN — PREFLIGHT REQUIRED | Official general fine-tuning support; PEFT targets and original-base adapter export not audited |
| Phi-4-reasoning-plus | UNCERTAIN — PREFLIGHT REQUIRED | Dense Phi3 targets plausible; original-base reset and complete adapter export unverified |

Support details were read at fixed commits: [GLM4 MoE Lite modeling](https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/models/glm4_moe_lite/modeling_glm4_moe_lite.py) has attention Linears and tensor-stacked experts; [PEFT LoRA configuration](https://github.com/huggingface/peft/blob/532a05dd505c28993119b7715ee286f4234bf51b/src/peft/tuners/lora/config.py) exposes parameter targeting; [vLLM model support](https://github.com/vllm-project/vllm/blob/5f30fc7031cae49bf51073fc953d419b08f8887c/docs/models/supported_models.md) declares direct LoRA for several relevant architectures. A blank table cell is absence of that declaration, not a proof that merge/export adaptation cannot work.

The [pinned fine-grained FP8 quantizer](https://github.com/huggingface/transformers/blob/02d8fb9784e8f14a1251e4c992cd82a5762417c6/src/transformers/quantizers/quantizer_finegrained_fp8.py) reports `is_trainable=False`; supported dequantization is a separate path to verify. Native FP8/MXFP4/other compressed storage cannot be treated as ordinary trainable BF16 merely because weights can be served. Conversion must derive from the same original identity; a separately published BF16 sibling is not silently the same experimental original.

The exact [Lightning LoRA guide](https://github.com/NVIDIA-NeMo/Nemotron/blob/8749344f8ccefd50181c56b013ddc5c8a6154a8c/usage-cookbook/Nemotron-3.5-Lightning/dgx-station-recipes/lora.md) explains why Mamba `out_proj` wrappers can be bypassed by kernels. Its data-history truncation policy is not adopted here. The [Megatron-Bridge Lightning guide](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/721356847b79c4bf78e5b8e9ceb6ed87835d3872/docs/models/nemotron/nemotron3.5-lightning.md) is upstream lifecycle support, not a project adaptation outcome. No claim that one model adapts better is made.

## 8. P — product-relevance table with evidence

PASS evidence below is a precise location/description, rather than a copied benchmark score. Qualifying intended use establishes A-type evidence; repository/SWE evaluation existence establishes B-type evidence. A training-data or decontamination mention does not establish B. Generic code/function evaluations and community experiments are insufficient.

| Checkpoint | P | Authoritative evidence / failed scope | Source |
| --- | --- | --- | --- |
| Qwen3-Coder-30B-A3B-Instruct | PASS | Agentic Coding feature; official coding-agent integration | [evidence](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/README.md) |
| Qwen3-Coder-Next | PASS | Specialized for coding agents, model-card Introduction | [evidence](https://huggingface.co/Qwen/Qwen3-Coder-Next/blob/a7fbcb5c0e12d62a448eaa0e260346bf5dcc0feb/README.md) |
| Qwen3-Coder-480B-A35B-Instruct | PASS | Agentic Coding feature | [evidence](https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct/blob/9d90cf8fca1bf7b7acca42d3fc9ae694a2194069/README.md) |
| Qwen3.8-27B | PASS | SWE-bench Pro evaluation, Language table | [evidence](https://huggingface.co/Qwen/Qwen3.8-27B/blob/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0/README.md) |
| Qwen3.8-Flash-Next | PASS | SWE-bench Pro and Multilingual evaluation, Language table | [evidence](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/de4b8e4d43b917e7706784d8bb445c9af86a3540/README.md) |
| Devstral-Small-2-24B-Instruct-2512 | PASS | Agentic LLM for software engineering; codebase exploration and multi-file editing, Introduction | [evidence](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/README.md) |
| Devstral-Small-2507 | PASS | Software-engineering agents; codebases and multi-file editing, Introduction | [evidence](https://huggingface.co/mistralai/Devstral-Small-2507/blob/bd165ab26cebbcc2eea2c4ecbfc07f3ac42b3c39/README.md) |
| Devstral-2-123B-Instruct-2512 | PASS | Software-engineering and coding-agent use, Introduction | [evidence](https://huggingface.co/mistralai/Devstral-2-123B-Instruct-2512/blob/1613bf01adb5e1c6fdc196b46e6b173eae75eb4a/README.md) |
| gpt-oss-20b | PASS | Official OpenAI model card section 2.6 explicitly reports SWE-bench Verified for both checkpoints | [evidence](https://deploymentsafety.openai.com/gpt-oss#evaluation) |
| gpt-oss-120b | PASS | Official OpenAI model card section 2.6 explicitly reports SWE-bench Verified for both checkpoints | [evidence](https://deploymentsafety.openai.com/gpt-oss#evaluation) |
| DeepSeek-V4.1-Flash | PASS | Code Agent benchmark methods including DeepSWE and NL2Repo, evaluation notes | [evidence](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/2cba9e42aa026125f3ed06c6d98c1db82f7ca027/README.md) |
| DeepSeek-V4-Flash-0731 | PASS | Code-agent benchmark evaluation documented in card | [evidence](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/7872f01b1d1fe23eabc4c98b48bffcef5a386062/README.md) |
| DeepSeek-V3.2 | PASS | SWE Verified and Multilingual evaluation, technical report section 4.1 | [evidence](https://arxiv.org/html/2512.02556v1#S4.SS1) |
| DeepSeek-Coder-V2-Lite-Instruct | PASS | Specific Lite-Instruct SWE-Bench row, official DeepSeek-Coder-V2 repository section 3.3 | [evidence](https://github.com/deepseek-ai/DeepSeek-Coder-V2/blob/a2b4e0a25b5dab1ee87e8080f76e4512b0725b7b/README.md#33-standard-code-benchmarks) |
| GLM-4.7-Flash | PASS | SWE Bench Verified evaluation, Evaluation Parameters section | [evidence](https://huggingface.co/zai-org/GLM-4.7-Flash/blob/7dd20894a642a0aa287e9827cb1a1f7f91386b67/README.md) |
| GLM-5.3-Flash | PASS | DeepSWE and NL2Repo evaluation footnotes | [evidence](https://huggingface.co/zai-org/GLM-5.3-Flash/blob/eb9eb208eb0d988989d07a6a12d0fdeb5f52574a/README.md) |
| GLM-5.3 | PASS | DeepSWE / FrontierSWE evaluation footnotes | [evidence](https://huggingface.co/zai-org/GLM-5.3/blob/aca966e4e02791568aa6a4ced368624b3d897f42/README.md) |
| Kimi-K3 | PASS | Coding Agent Framework section | [evidence](https://huggingface.co/moonshotai/Kimi-K3/blob/f831ab66814297da540d832a5235f8e904f29d06/README.md) |
| Kimi-K2.7-Code | PASS | Coding-focused agentic model for complex software-engineering workflows, Introduction | [evidence](https://huggingface.co/moonshotai/Kimi-K2.7-Code/blob/74797c9c62378b951a1f6fcf5c4631024e9b8bef/README.md) |
| Kimi-Linear-48B-A3B-Instruct | FAIL | Inspected card documents general reasoning/long-context/RL tasks; no SWE/coding-agent use or repository benchmark established | [evidence](https://huggingface.co/moonshotai/Kimi-Linear-48B-A3B-Instruct/blob/e1df551a447157d4658b573f9a695d57658590e9/README.md) |
| Kimi-Dev-72B | PASS | Open-source coding LLM for software-engineering tasks, Introduction | [evidence](https://huggingface.co/moonshotai/Kimi-Dev-72B/blob/8791d7981945752a51f692d66f2bbfb3573c9722/README.md) |
| MiniMax-M3 | PASS | Long-horizon agentic coding capability, Highlights | [evidence](https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/f0e1c1e04d40177e4673a22097036854f536e9c0/README.md) |
| MiniMax-M2.7 | PASS | Coding/software-engineering and SWE-bench evaluation documented in card | [evidence](https://huggingface.co/MiniMaxAI/MiniMax-M2.7/blob/d494266a4affc0d2995ba1fa35c8481cbd84294b/README.md) |
| NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | PASS | SWE-Bench Verified and Terminal-Bench coding-agent results, Agentic Coding Benchmarks section | [evidence](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16/blob/a9904d24bcc1d289a1950fa9d2b978c47cf903b9/README.md) |
| NVIDIA-Nemotron-3-Super-120B-A12B-BF16 | PASS | SWE Bench Verified and Multilingual evaluation scaffold notes | [evidence](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16/blob/2dc98e2afe4face0e4ce40972a915c45368bd34a/README.md) |
| NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 | PASS | SWE-Bench Verified and Multilingual, official technical report Table 10 | [evidence](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf) |
| gemma-4-31B-it | PASS | Official Hugging Face release guide, co-developed with Google: Llama.cpp / Plug in your local agent sections explicitly document coding agents including Pi and OpenCode | [evidence](https://huggingface.co/blog/gemma4#plug-in-your-local-agent) |
| gemma-4-26B-A4B-it | PASS | Official Hugging Face release guide, co-developed with Google: Llama.cpp / Plug in your local agent sections explicitly document coding agents including Pi and OpenCode | [evidence](https://huggingface.co/blog/gemma4#plug-in-your-local-agent) |
| Llama-4-Scout-17B-16E-Instruct | FAIL | Official card does not establish SWE/coding-agent use or recognized repository evaluation | [evidence](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct/blob/92f3b1597a195b523d8d9e5700e57e4fbb8f20d3/README.md) |
| Olmo-3-32B-Think | FAIL | General math/coding thinking and function-level evaluations; required SWE evidence not established | [evidence](https://huggingface.co/allenai/Olmo-3-32B-Think/blob/f2edda15216e738ef2bb73771e11890e152b2112/README.md) |
| MiniMax-M2.5 | PASS | Specific SWE-bench evaluations in official card | [evidence](https://huggingface.co/MiniMaxAI/MiniMax-M2.5/blob/f710177d938eff80b684d42c5aa84b382612f21f/README.md) |
| granite-4.1-30b | FAIL | Inspected 4.1 card has generic tool/instruction/coding evidence, not required SWE gate; no inheritance from 4.2 | [evidence](https://huggingface.co/ibm-granite/granite-4.1-30b/blob/4fae6278f7132abf5e971f9de49ebbad09c54cce/README.md) |
| phi-4 | FAIL | Generic reasoning/function coding evidence does not establish SWE gate | [evidence](https://huggingface.co/microsoft/phi-4/blob/2db69c1c3e91a05d2c64a3185acfbaf36f744e25/README.md) |
| granite-4.2-8b | PASS | SWE Bench Verified/Pro/Multilingual evaluation plus Using with Agentic Coding Harnesses | [evidence](https://huggingface.co/ibm-granite/granite-4.2-8b/blob/f8de16cdcdbc6c779ca517604e050d82cc119e44/README.md) |
| Olmo-3.1-32B-Instruct | FAIL | Current 3.1 card establishes generic coding and instruction/function benchmarks, not required SWE evidence | [evidence](https://huggingface.co/allenai/Olmo-3.1-32B-Instruct/blob/ac0587e4a7744a551c059d8cd17ba220bc940dae/README.md) |
| Phi-4-reasoning-plus | FAIL | Official card has generic coding/function evaluations; technical report mentions SWE-bench in decontamination, which does not establish an evaluation or intended coding-agent use | [evidence](https://huggingface.co/microsoft/Phi-4-reasoning-plus/blob/69baf8528e1bcf05f475034d9e5dd32875ed125f/README.md) |

Gemma PASS uses the official Hugging Face release/integration guide co-developed with Google, especially “Llama.cpp” and “Plug in your local agent.” It is publisher-side release documentation, not a community anecdote or a copied quality result. The 26B coding-agent integration is explicit and the family guide applies to Gemma4's local deployment. The card alone would not establish this gate. Granite4.2's current card meets the gate; Granite4.1 does not inherit its successor's evidence.

## 9. Resource-regime table

Selected checkpoint package sizes below are declared safetensor bytes, in decimal GB. They exclude tokenizer/runtime/activation/cache/optimizer overhead. Alternate consolidated versus HF shard packaging is not summed: Devstral Small2 has approximately 25.793GB of selected HF shards, Small2507 47.145GB, and 123B approximately 128.250GB. Counting both packaging paths would double those models. Native compressed size is not dense training residency. Labels describe plausible engineering classes; they are not measured fits or exclusion ceilings.

| Checkpoint | Selected package GB | Inference regime | Adaptation regime |
| --- | --- | --- | --- |
| Qwen3-Coder-30B-A3B-Instruct | 61.067 | single large-memory accelerator | single large-memory / small multi-GPU |
| Qwen3-Coder-Next | 159.358 | small multi-GPU | small multi-GPU |
| Qwen3-Coder-480B-A35B-Instruct | 960.314 | large multi-GPU / cluster-scale | cluster-scale |
| Qwen3.8-27B | 55.563 | single large-memory accelerator | single large-memory / small multi-GPU |
| Qwen3.8-Flash-Next | 360.000 | small / large multi-GPU plus substantial host-memory offload | large multi-GPU / specialized |
| Devstral-Small-2-24B-Instruct-2512 | 25.793 | single large-memory accelerator; quantized deployment may use a smaller device | single large-memory / small multi-GPU after supported original-checkpoint conversion |
| Devstral-Small-2507 | 47.145 | single large-memory accelerator | single large-memory / small multi-GPU |
| Devstral-2-123B-Instruct-2512 | 128.250 | large multi-GPU | large multi-GPU / cluster-scale |
| gpt-oss-20b | 13.761 | single modest / large-memory accelerator depending on native MXFP4 or BF16 | single large-memory / small multi-GPU |
| gpt-oss-120b | 65.249 | single large-memory accelerator for native package / multi-GPU BF16 | large multi-GPU |
| DeepSeek-V4.1-Flash | 510.297 | large multi-GPU / specialized plus conditional-memory offload | cluster-scale / specialized |
| DeepSeek-V4-Flash-0731 | 166.887 | large multi-GPU / specialized | cluster-scale / specialized |
| DeepSeek-V3.2 | 689.483 | large multi-GPU / cluster-scale | cluster-scale |
| DeepSeek-Coder-V2-Lite-Instruct | 31.414 | single large-memory accelerator; compressed variants may be modest | single large-memory / small multi-GPU |
| GLM-4.7-Flash | 62.444 | single large-memory / small multi-GPU | single large-memory / small multi-GPU |
| GLM-5.3-Flash | 328.337 | large multi-GPU | large multi-GPU / cluster-scale |
| GLM-5.3 | 755.632 | large multi-GPU / cluster-scale | cluster-scale |
| Kimi-K3 | 1560.936 | cluster-scale / specialized | cluster-scale / specialized |
| Kimi-K2.7-Code | 595.178 | large multi-GPU / cluster-scale | cluster-scale |
| Kimi-Linear-48B-A3B-Instruct | 98.248 | small multi-GPU | small / large multi-GPU |
| Kimi-Dev-72B | 145.413 | small multi-GPU | small multi-GPU |
| MiniMax-M3 | 854.176 | large multi-GPU / cluster-scale | cluster-scale |
| MiniMax-M2.7 | 230.134 | large multi-GPU | large multi-GPU / cluster-scale |
| NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | 65.827 | single large-memory accelerator | single specialized large-memory accelerator / small multi-GPU |
| NVIDIA-Nemotron-3-Super-120B-A12B-BF16 | 247.228 | small / large multi-GPU | large multi-GPU |
| NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 | 1121.056 | large multi-GPU / cluster-scale | cluster-scale |
| gemma-4-31B-it | 62.546 | single large-memory accelerator | single large-memory / small multi-GPU |
| gemma-4-26B-A4B-it | 51.612 | single large-memory accelerator | single large-memory / small multi-GPU |
| Llama-4-Scout-17B-16E-Instruct | 217.284 | small multi-GPU | small / large multi-GPU |
| Olmo-3-32B-Think | 64.467 | single large-memory accelerator | single large-memory / small multi-GPU |
| MiniMax-M2.5 | 230.134 | large multi-GPU | large multi-GPU / cluster-scale |
| granite-4.1-30b | 57.732 | single large-memory accelerator | single large-memory / small multi-GPU |
| phi-4 | 29.319 | single large-memory accelerator | single large-memory / small multi-GPU |
| granite-4.2-8b | 17.583 | single modest accelerator | single modest / large-memory accelerator depending on training sequence and state |
| Olmo-3.1-32B-Instruct | 64.467 | single large-memory accelerator | single large-memory / small multi-GPU |
| Phi-4-reasoning-plus | 29.319 | single large-memory accelerator | single large-memory / small multi-GPU |

Examples of source/card distinctions: Devstral Small2 advertises 256k while its pinned text config says 393216; V3.2/Coder-V2 advertise 128k while configs say 163840; Nemotron cards describe extended 1M while native configs say 262144; Granite4.2's extension claim is distinct from native 131072. None authorizes an extension or proves the study's usable budget.

Conditional memory deserves explicit accounting: Qwen Flash Next's active backbone count omits substantial lookup/PLE and MTP storage; DeepSeek V4.1's Engram has its own residency/offload; KimiK3's native compression does not make its logical multi-trillion base small to rebuild. Full context attention needs KV cache; DeltaNet/Mamba hybrids also need recurrent state and attention cache. Host offload, TP/CP/EP sharding, and quantization alter topology and repeated-cycle work. No accelerator price, spending estimate, throughput, or hard fit limit is asserted.

## 10. Lineage groups

Use all four dimensions together: architecture/base, documented checkpoint training ancestry, tokenizer/serialization, and runtime/adaptation. The family map in section 4 is a census grouping, not an equivalence partition that makes all its members redundant. The CSV gives finer mechanism groups and each exact config.

| Comparison | Architecture / training lineage | Tokenizer / serialization | Runtime / adaptation consequence |
| --- | --- | --- | --- |
| Qwen30 / Next | Full-attention MoE versus DeltaNet/full-attention hybrid MoE; independent checkpoints | Shared Qwen BPE/ChatML does not erase architecture | Different recurrent state, target coverage, residency and export/serving paths |
| Qwen30 / 480B | Related full-attention MoE family, separately trained size checkpoint | Same serialization family | Cluster original-base reload/sharding versus smaller-cycle regime; size alone is not the argument |
| Qwen3.8 dense / Flash Next | Dense DeltaNet versus QSA/gated/conditional-memory MoE | New generation template/tokenizer details, exact identity required | Dense PEFT versus special conditional-memory targeting/offload; different terms |
| Devstral2507 / Small2 /123B | Mistral dense SWE post-training; 2507 documented MistralSmall3.1 derivative; Small2 retains multimodal artifact | Tekken/Mistral instruction family, not necessarily identical exact template | BF16 versus FP8 same-original conversion; vision exclusions; large dense distributed state |
| DeepSeekV2Lite /V3.2 /V4/V4.1 | MLA→DSA/MLA→CSA/mHC→CSA2/Engram; not one same subject | V2 template versus revised protocol-aware encoding | Low-rank projections/expert targeting, sparse/compressed backward and quantization differ |
| GLM4.7 /5.3Flash /5.3 | MLA small versus sparse-linear/mHC and large DSA branches | Different native template/multimodal generations | BF16 attention PEFT versus new FP8/hybrid/export and cluster plan |
| KimiDev /Qwen coding roster | Documented Qwen2.5-72B dense ancestor; not Qwen3 MoE | Qwen2 BPE/ChatML | Independent dense-large adaptation regime despite non-Qwen publisher |
| KimiK2.7 /K3 /Linear | K2.5/2.6 MLA architecture reused versus KDA/latentMoE/AttnRes versus experimental KDA+MLA | Kimi channels; K3 always-thinking requirement differs | Compressed trillion-scale conversion versus KDA backward and mandatory-stream uncertainty |
| MiniMaxM2.5 /M2.7 /M3 | M2 full-attention expert family versus sparse-attention multimodal head | M2 versus M3 template and reasoning modes | Native FP8 versus large BF16 sparse path; license is checkpoint-specific |
| NemotronLightning /Super /Ultra | Mamba2 expert family; larger heads add latent expert structures | Nemotron configurable-thinking templates | Fused-kernel target exclusions; different latent targets, distributed base state and terms |
| Gemma4 dense /MoE | Same multimodal family, dense versus routed expert representation | Gemma native thought/final/turn channels | Different expert adaptation and resident package; multimodal training targets excluded explicitly |
| Granite4.1 /4.2 | Dense Granite models; exact public configs distinguish scale/post-training | Granite/default reasoning template details | 30B versus modest 8B-cycle residency; successor has independent P evidence |
| OLMo3 /3.1; Phi4 /reasoning-plus | Documented same base lineage with new post-training | Think versus instruction/reasoning templates | Different context/output behavior, not automatically equivalent subject |

Where an exact training ancestor is not documented, it remains unspecified. Similar model_type or common tokenizer is not substituted for known training lineage. No expected adaptation improvement is part of these comparisons.

## 11. Redundancy decisions

**No census row is assigned REDUNDANT REPRESENTATIVE.** The strict four-dimension equivalence rule is not sufficiently established for the useful comparisons. In particular, the current Qwens are not redundant; Gemma dense/MoE, small/large Devstral, MLA/CSA DeepSeek, and Lightning/latent Nemotron materially change a mechanism or resource/serialization regime.

Avoiding dozens of trivial packaging/post-training variants is census grouping, not a scored exclusion or an assertion that those variants satisfy the frozen redundancy rule. Native BF16 versus separately quantized exports and alternative shard packaging are recorded as artifact distinctions; only one original checkpoint identity per listed subject is evaluated. Kimi K2.5/2.6 are ancestors represented in the current coding-lineage census, not individually rejected. Optional subjects are not called redundant merely because a minimum coverage set does not include them.

## 12. Current-roster coverage analysis

Qwen3-Coder-30B-A3B covers full-attention routed MoE with ordinary attention/expert target paths and approximately 61GB BF16 original residency. Next covers a hybrid of full attention and DeltaNet recurrence with MoE, approximately 159GB BF16 residency, different state isolation, and different adaptation/serving integration. Their shared serialization gives limited protocol diversity, but their architecture and repeated-load resource regimes differ materially. These are historical static conclusions; their preflights were not rerun.

The most obvious independent missing primitive adaptation regimes are ordinary dense attention/MLP, MLA with low-rank attention projections and tensor-stacked experts, and Mamba2 with fused state-space kernels. Devstral Small2, GLM4.7Flash, and Lightning respectively expose those gaps while also adding Mistral, GLM, and Nemotron serialization. One cannot replace another: dense PEFT does not validate MLA projection/expert targeting; neither validates Mamba's wrapper-bypassing kernels. Next's DeltaNet path does not certify Mamba.

Gemma channels, Granite modest dense residency, dense DeltaNet, latent expert heads, CSA/QSA, and conditional-memory lookup remain independently useful sensitivity regimes. The minimum proposal samples the core mechanism gaps, not every mechanism×serialization×resource cross-product. Their omission limits breadth claims and is explicitly visible; no blanket claim of representation of all open models or every frontier architecture is justified. Models lacking an evidenced repeated original-base route remain engineering references; they are not excluded merely for being large.

## 13. Final disposition table

Only the five requested disposition labels are used. “Historical completed” identifies a retained full-preflight path that needs no new static work. “Optional” and “reference” are work-state annotations, not additional dispositions. INFERENCE-ONLY REFERENCE is a provisional role outside the *currently evidenced* repeated-cycle plan: no exact project topology/reset/export plan has been supplied for those complex distributed or specialized originals. It is not an A FAIL, hardware-ceiling rejection, or proof they cannot be trained. A documented pre-outcome cycle plan can promote a reference without using outcomes.

| Checkpoint | Disposition | Work state | Reason |
| --- | --- | --- | --- |
| Qwen3-Coder-30B-A3B-Instruct | FULL PREFLIGHT | completed_historical | Baseline full-attention routed-expert regime; no new static preflight |
| Qwen3-Coder-Next | FULL PREFLIGHT | completed_historical | Independent DeltaNet-plus-MoE mechanism and larger resident base; verify after 30B |
| Qwen3-Coder-480B-A35B-Instruct | INFERENCE-ONLY REFERENCE | landscape_only | Resource reference; not redundant with 30B because cluster-scale training residency differs |
| Qwen3.8-27B | TARGETED PREFLIGHT | optional_not_minimum | Useful dense-recurrent interaction, but minimum covers recurrence and density separately; not declared redundant |
| Qwen3.8-Flash-Next | TARGETED PREFLIGHT | license_and_support_only_not_minimum | Material new mechanism remains visible; licensing and specialized rebuild support unresolved; no automatic product eligibility |
| Devstral-Small-2-24B-Instruct-2512 | FULL PREFLIGHT | minimum_full | Adds ordinary dense adaptation and Mistral serialization; newest weights require full static preflight, not blanket Apache-plus-LoRA admission |
| Devstral-Small-2507 | FULL PREFLIGHT | conditional_dense_fallback | Conditional fallback only if Small 2 lacks a same-original-base adaptation path; not redundant with its FP8/multimodal successor |
| Devstral-2-123B-Instruct-2512 | TARGETED PREFLIGHT | license_and_conversion_only_not_minimum | Revenue condition must be resolved before eligibility; independent resource regime, not a redundant small-model variant |
| gpt-oss-20b | EXCLUDE | historical_protocol_drop | Historical tested protocol boundary; exclusion is path-specific, not an architectural impossibility claim |
| gpt-oss-120b | EXCLUDE | same_proposed_projection_not_admitted | No new Harmony audit or attempt to retain this path |
| DeepSeek-V4.1-Flash | INFERENCE-ONLY REFERENCE | specialized_reference | Contemporary architecture reference; not evidence of a practical repeated adaptation loop or a hard hardware exclusion |
| DeepSeek-V4-Flash-0731 | INFERENCE-ONLY REFERENCE | specialized_reference | Different compression/quantization regime from V4.1; grouped census family, not called redundant |
| DeepSeek-V3.2 | INFERENCE-ONLY REFERENCE | large_reference | MLA/DSA cluster resource reference; smaller MLA subjects below can screen mechanism without committing to cluster cycles |
| DeepSeek-Coder-V2-Lite-Instruct | FULL PREFLIGHT | optional_MLA_alternative | Legacy but still obtainable small MLA alternative; retain if GLM protocol gate fails, rather than pretending newer is necessarily eligible |
| GLM-4.7-Flash | TARGETED PREFLIGHT | minimum_targeted | Adds MLA parameterization and GLM serialization; targeted native-profile check can change classification |
| GLM-5.3-Flash | INFERENCE-ONLY REFERENCE | specialized_reference | Not redundant with Flash 4.7: new architecture and much larger resident base |
| GLM-5.3 | TARGETED PREFLIGHT | terms_only_then_reference_not_minimum | Resolve applicability of terms, then keep as large resource reference; no license shortcut from GLM4.7 MIT |
| Kimi-K3 | TARGETED PREFLIGHT | terms_and_mandatory_reasoning_only_not_minimum | Current head included; neither automatically eligible nor excluded solely for size |
| Kimi-K2.7-Code | INFERENCE-ONLY REFERENCE | large_reference | Current coding checkpoint covers K2.5/K2.6 family at census level; no claim all variants meet redundancy rule |
| Kimi-Linear-48B-A3B-Instruct | EXCLUDE | P_gate_not_established | Independent mechanism, excluded by mechanical P evidence gate rather than vendor or quality |
| Kimi-Dev-72B | FULL PREFLIGHT | optional_dense_large | Non-Qwen publisher does not create independent architecture; also not redundant with current Qwen3 MoEs because density/training differs |
| MiniMax-M3 | TARGETED PREFLIGHT | terms_only_then_reference_not_minimum | Not an MIT license; terms-only targeted check precedes any reference path |
| MiniMax-M2.7 | EXCLUDE | unqualified_commercial_product_path_fails | Exclude unqualified primary research/product-development path; non-commercial research is a separate permitted scope, not silently substituted |
| NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 | TARGETED PREFLIGHT | minimum_targeted | Adds Mamba2 state and custom-kernel adapter regime; targeted stream/determinism/coverage check rather than borrowing DeltaNet evidence |
| NVIDIA-Nemotron-3-Super-120B-A12B-BF16 | INFERENCE-ONLY REFERENCE | large_reference | Reference under currently evidenced repeated-loop plan; can be promoted with a pre-outcome distributed-cycle plan, no hard resource ceiling |
| NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 | INFERENCE-ONLY REFERENCE | large_reference | Latent expert and cluster state regime differs from Lightning; not declared redundant |
| gemma-4-31B-it | TARGETED PREFLIGHT | optional_Gemma_channel_boundary | Eligible independent serialization regime; optional targeted channel-boundary check, not a generic-coding P exclusion or redundant representative |
| gemma-4-26B-A4B-it | TARGETED PREFLIGHT | optional_Gemma_channel_boundary | Eligible independent serialization regime; optional targeted channel-boundary check, not a generic-coding P exclusion or redundant representative |
| Llama-4-Scout-17B-16E-Instruct | EXCLUDE | P_gate_not_established_and_access_terms | No assumption that open weights imply Apache/MIT or automatic access |
| Olmo-3-32B-Think | EXCLUDE | P_gate_not_established | Open training artifacts do not replace mechanical P gate |
| MiniMax-M2.5 | INFERENCE-ONLY REFERENCE | large_reference | Retains licensable older-family reference so M2.7 terms do not exclude all MiniMax models |
| granite-4.1-30b | EXCLUDE | P_gate_not_established | Kept as release-lineage contrast; replaced in current-family census by 4.2 evidence, not excluded using scores |
| phi-4 | EXCLUDE | context_and_P_gate_fail | Source-based context exclusion, not coding-quality judgment |
| granite-4.2-8b | TARGETED PREFLIGHT | optional_dense_modest | New current IBM head included; modest dense resource sensitivity remains optional and untested, not declared redundant |
| Olmo-3.1-32B-Instruct | EXCLUDE | P_gate_not_established | Current family head checked; P failure is documented evidence scope, not inherited from 3.0 or a quality judgment |
| Phi-4-reasoning-plus | EXCLUDE | P_gate_not_established | Current reasoning derivative inspected; training/decontamination mentions do not pass mechanical P |

## 14. Tiebreak analysis

**NOT APPLIED.** No actual resource constraint requiring fewer surviving preflights was supplied. The three-item recommendation is a mechanism-gap work plan, not a ranking of survivors or a resource-elimination contest. Other dense/MLA representatives remain unresolved alternatives rather than invented losers. If a later concrete resource constraint requires choosing between non-redundant subjects, apply the requested lexicographic sequence: architecture/adaptation coverage → serialization coverage → adaptation-resource coverage → inference-resource coverage; then evidence of testable fresh-base adaptation; then unresolved verification burden; then documented resource burden. Retain both if still tied. Never add benchmark magnitude, expected adaptation quality, or a weighted score.

## 15. Minimum additional preflight recommendation

**Three bounded static work items before GPU spending. Do not begin them as infrastructure tests in this audit.**

| Subject | Work | Coverage-changing fact | Required static deliverable |
| --- | --- | --- | --- |
| Devstral-Small-2-24B-Instruct-2512, pinned SHA in section 3 | FULL PREFLIGHT | Dense SWE original plus Tekken/Mistral serialization; native FP8 may prevent the required adaptation lifecycle | Exact text-only template/token/terminal accounting; deployed 32768/2048 and greedy-control mapping; pinned loader/serving stack; deterministic same-original-checkpoint dequantization route; explicit attention/MLP targets excluding modality components; adapter save/reload and original-base merge/export format; complete offline/no-read/no-tools profile; reset/load and package map |
| GLM-4.7-Flash, pinned SHA in section 3 | TARGETED PREFLIGHT | MLA projection and stacked expert representation, plus native GLM think-prefix behavior | Establish whether a documented native generation-input mode is allowed by unchanged draft3; enumerate the entire emitted suffix and real EOS/tool-handoff tokens without generation; map MLA q_a/q_b/kv_a/kv_b/o Linears and expert 3D parameters to PEFT/direct-serving formats; declare attention-only versus expert scope; certify the static original-base reset/save/reload/export plan |
| NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, pinned SHA in section 3 | TARGETED PREFLIGHT | Mamba2 kernel-aware adaptation, recurrent state, and determinism independent of DeltaNet | Validate native input profile under draft3 without output reasoning extraction; identify all emitted native boundaries; map safe projections/expert targets and Mamba out_proj exclusions to actual kernel calls; preserve original identity through NeMo/Megatron adapter reload/export; document fresh SSM/KV state reset, MTP/speculation disabled or semantically controlled, and deterministic cache representation |

Use only small immutable public text/metadata for these deliverables. A static preflight may identify but cannot empirically certify long-context memory, repeatability, or replacement-output validity. Those remain later infrastructure admission checks, after the bounded static work. Do not execute upstream recipes, instantiate adapters, create synthetic model outputs, or inspect project tasks for this work.

For GLM/Nemotron/Gemma/Granite/Qwen-thinking templates, the fact that `enable_thinking=False` exists does not establish protocol permission. Examine input construction and the full emitted stream; do not choose a disabled-reasoning mode merely to fit the reserve. If the only usable path needs suppression, final-only projection, retries, different effort, clipping, or budget accommodation, mark that path incompatible under unchanged draft3. A refusal of that profile is not an architectural A failure.

The Lightning one-H100 example uses FP16 SSM cache with stochastic rounding. Greedy token selection alone does not settle bit-level repeatability. Determine whether a documented deterministic cache alternative exists without changing the study semantics; if it does not, retain I UNCERTAIN or fail the proposed path. The station LoRA recipe's history truncation and old-reasoning removal are not adopted. Kernel target exclusions must be reported as adaptation scope, not silently treated as all-module LoRA.

**Conditional replacements, not an expanding shopping list:** if Small2 has no technically credible conversion from its own original FP8 artifact, full-preflight the already enumerated Devstral-Small-2507 BF16 original as a distinct fallback, with its exact identity; do not silently switch originals. If GLM's only protocol path is impermissible, full-preflight the already enumerated BF16 DeepSeek-Coder-V2-Lite-Instruct as the MLA alternative, with its distinct license/template. There is no automatic Mamba fallback: an exact source-based block is recorded rather than moving indefinitely up the size ladder.

The three work items are necessary for three independent gaps; one or two cannot establish all three. This is a minimal covering work set under the stated core mechanism scope, not a theorem that these exact representatives uniquely dominate all other survivors. Gemma native channels are an optional targeted sensitivity check if the proposed non-Qwen serialization checks cannot support the intended protocol-breadth claim; Granite4.2 is an optional modest-dense resource sensitivity. A newly verified feasible conditional-memory or latent-expert route must be treated as a named additional scope decision before any claim of comprehensive regime coverage. No resource tiebreak is smuggled into these alternatives.

## 16. Product adaptation-economics observations

Inference active parameters measure computation, not all resident original weights. Frozen PEFT still needs base weights and activation/backward propagation; a small routed active count does not shrink reload/export of all experts. Native quantized inference fit does not imply quantized training or same-original merge support.

| Burden | Dense BF16 / ordinary PEFT | MoE, recurrent, compressed, or conditional-memory route |
| --- | --- | --- |
| Inference residency | Full dense base plus KV and runtime workspace | All expert/base storage plus routing, KV/recurrent state, lookup memory or offload; active count is insufficient |
| Training residency | Frozen base plus activations and adapter gradients/optimizer | Frozen all-expert base plus sharded state and activation/routing/recurrent backward support; conversion may increase storage |
| Adapter state | Explicit target shapes and rank, not just total model count | Attention-only versus per-expert/parameter targets changes scale; fused tensor layout changes admissible targets |
| Reload each cycle | Verify exact original hash and discard prior adapted weights/state | Distributed reconstruction/offload and quantization provenance; fresh optimizer/RNG and base identity across workers |
| Merge/export | May allocate a full copy and write a whole dense checkpoint | Expert shards, custom kernels, latent/lookup components and quantized re-export may require special serialization |
| Operations | Simpler process/config/reset lifecycle is plausible, not measured | TP/CP/EP coordination, cache determinism, checkpoint I/O and compatible adapter serving add dependencies |

For a linear weight with dimensions m×n, ordinary LoRA contributes r(m+n) trainable parameters. For E independently adapted experts the corresponding contribution scales with E, unless the implementation explicitly shares adapters; do not assume active experts reduce saved adapter state. A stacked 3D expert tensor must be mapped to PEFT's actual parameter semantics before counting it.

Illustrative arithmetic only, not a selected adapter: Devstral-Small-2507's pinned dense config has 40 layers, hidden size 5120, 32 query heads, 8 KV heads, and head dimension 128. At hypothetical rank 16, q/k/v/o targets would have 19,660,800 adapter parameters: about 37.5 MiB for BF16 adapter weights. Adding gate/up/down targets with intermediate size 32768 would total 92,405,760 parameters, about 176.25 MiB BF16. If adapter weights, gradients, FP32 master copy and two FP32 Adam states total 16 bytes/parameter, these examples consume approximately 300 MiB and 1.377 GiB respectively, before activations, frozen base, workspace and distribution overhead. The rank/targets/optimizer are examples, not protocol decisions; no adapter was constructed.

For frozen BF16 weights, approximately 2N bytes of base residency is a lower-order starting estimate; package bytes include headers and may include modality/MTP tensors. Actual topology also depends on activations at the intended adaptation sequence length, sharding/offload, backward kernels, cache configuration and merge peaks. Do not silently impose the 32768 generation capacity as an adaptation truncation policy. Repeated-loop economics must include original reload, reconstruction, adapter-state reset, adapter reload and merge/export I/O, not only one forward pass. Without an actual topology and measurements, no cloud-price or cost ranking is warranted.

## 17. Remaining uncertainties

1. Public listed weights are not body-verified local originals. Exact metadata SHA/LFS values are recorded, but no model was loaded; access acceptance remains unresolved for Llama4.
2. No new checkpoint has empirical deployed-capacity, deterministic-replay, full replacement, EOS/hand-off, or offline-isolation certification. Nominal context and a greedy flag are insufficient.
3. Native input modes and emitted reasoning/channel syntax require protocol adjudication without changing draft3. No blanket non-thinking exemption is granted. Mandatory-thinking KimiK3 remains an explicit unresolved boundary.
4. Native quantization conversion/backward, stacked/fused targets, exact safe module coverage, fresh-original loading, saved-adapter roundtrip and export support are static plausibility findings, not executed project facts.
5. Several community licenses depend on organizational/product revenue, geography, distribution and service scope. No undisclosed fact is assumed, no license authorization requested, and no model publisher contacted. Stated use restrictions remain obligations even where eligibility passes.
6. INFERENCE-ONLY REFERENCE reflects absence of an evidenced exact repeated-cycle plan for complex distributed/specialized originals; it must not become a permanent size exclusion. The audit cannot certify an undisclosed infrastructure budget. References with A PASS are technically plausible but outside the currently documented project cycle plan, not adaptation-incapable.
7. Some primary reports were consulted through the web tool without a locally archived body; the manifest explicitly records that limitation. Public live pages are date/hash snapshots rather than immutable publisher versions. Missing text files and failed documentation paths remain unavailable, not filled from memory.
8. Optional survivors and architecture interactions are not fully covered by the proposed minimum. The broad census supports stopping open-ended shopping under the bounded primitive-mechanism claim; comprehensive serialization, conditional-memory, latent-MoE or all-size claims require explicit further scope decisions. This uncertainty is not concealed by declaring those models redundant.
9. A PASS says testability, P PASS says authoritative SWE relevance, and I PASS says static admissibility. None is a prediction about coding quality, adaptation gain, economic viability, or generalization beyond the eventual measured roster.

## 18. Candidate artifacts inspected?

**NO.** Neither Step8K candidate inventories/dispositions nor the 31 candidate conventions were opened. No benchmark/project task instances, Study1 outcomes, project model outputs, private evaluators or scorers were inspected. Project input was limited to the two supplied attachments, the historical cross-model audit report, and repository identity/status/instruction-path checks. Public vendor benchmark names/method descriptions were read only to establish P; project evaluations were not run.

## 19. Model inference performed?

**NO.** No weights downloaded, no model/tokenizer loaded, no generation, no GPU infrastructure tests, no training, and no adapter instantiated. Selected upstream Python files were read as text, not executed. Only standard-library metadata acquisition/report generation and artifact-integrity checks ran.

## 20. Protocol modified?

**NO.** Draft2, current-repo-v1-draft3, context-policy implementation, and the historical Harmony completion decision were not edited. No protocol or final roster was frozen. Qwen infrastructure order was preserved. No commit was made.

## 21. Files created/modified

All audit writes are inside `experiments/model_preflight/landscape_closure/`:

- `REPORT.md`: all 23 requested sections.
- `landscape.csv`: 36 rows with exact identities, separate five eligibility subgates, I/A/P, resource/lineage/serialization, allowed disposition and evidence links; no benchmark-score field.
- `source_manifest.json`: primary-source retrieval/identity/hash/status records, historical input identity, acquisition constraints, and web-only consultation limitations.
- `artifact_manifest.json`: relative file paths, lengths and SHA-256 for every generated/archive file except itself; self-exclusion avoids a recursive hash definition.
- `decisions.json`: readable manual decisions underlying the CSV/report.
- `collect_sources.py`, `collect_support.py`, `build_artifacts.py`, `validate_artifacts.py`: bounded text acquisition, deterministic report construction and integrity checks; they do not import model code.
- `sources/`: archived small public model/support text and metadata, plus byte-identical supplied audit/request input copies.
- `validation.json`: row/schema/identity/cutoff/hash/package and tracked-repository integrity checks.

Existing preflight artifacts were retained. HEAD/tracked-file checks and exact source/body-size checks are recorded in validation. No application/private evaluation test was necessary or permitted for a documentation-only audit.

## 22. STOP-MODEL-SHOPPING determination

**Conditional YES after the section15 bounded static queue; NO unconditional roster closure today.** Stop open-ended discovery/ranking once each of dense, MLA, and Mamba is either represented by a statically admissible fresh-base path or has a precise source-based failure with the named fallback checked where applicable. Record the optional/reference scope and limit conclusions to mechanisms actually retained and later admitted. A failed path is evidence about that path; it does not justify claiming the missing architecture was tested.

Before asserting the conditional stop has been reached, each work item must name its original SHA, eligibility/I/A/P classification, exact native-stream profile without unauthorized projection, safe adaptation targets and original-base lifecycle, descriptive topology, and remaining empirical infrastructure checks. If a conditional license or specialized training fact resolves in favor of an independently feasible conditional-memory, latent-expert or additional native-channel regime *and that regime is required for the project's breadth claim*, resolve that specific known scope gap before closure. The three preflights therefore do not guarantee unconditional closure regardless of what they discover.

No count of survivors is required. Optional Gemma/Granite/dense-DeltaNet sensitivities may remain outside the minimum with explicit claim limitations; that is not a redundancy determination. Reopen discovery only for a concrete factual blocker in an intended admission or an actually material new release/regime under a stated cutoff revision. Do not reopen because of benchmark magnitudes, anticipated adaptation results, or a desire for a more impressive roster. No future monitor/automation is created by this audit.

## 23. Final recommendation

Complete the three additional **static** work items, using only public immutable text, before authorizing GPU spending. Keep Devstral BF16 and DeepSeek V2 Lite as named conditional substitutes, not silent checkpoint swaps. Preserve the two Qwen historical proceed states and 30B→Next infrastructure order; preserve the gpt-oss20b final-only Harmony DROP. Keep terms-sensitive and specialized families visible as unresolved/reference subjects, and optional Gemma/Granite coverage explicit.

The audit establishes a broad, source-grounded landscape and a bounded mechanism-gap plan. It does not admit a new model, certify infrastructure, select a quality winner, change the protocol, commit changes, or freeze the roster. Stop broad shopping after the bounded plan satisfies the conditional coverage criterion in section22; report any surviving distinct feasible gap rather than inventing closure.
