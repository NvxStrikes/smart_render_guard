<div align="center">

# 🛡️ SMART RENDER GUARD LITE

### *The Intelligent Crash Scanner & Memory Optimizer for Blender*

[![Blender 3.6 - 5.x](https://img.shields.io/badge/Blender-3.6%20%7C%204.x%20%7C%205.x-E87D0D?style=for-the-badge&logo=blender&logoColor=white)](https://www.blender.org/)
[![License GPLv3](https://img.shields.io/badge/License-GPL%20v3-007ACC?style=for-the-badge&logo=gnu&logoColor=white)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-4EBA6F?style=for-the-badge)](https://github.com/NvxStrikes/smart_render_guard)
[![Status](https://img.shields.io/badge/Edition-Lite%20(Open%20Source)-blueviolet?style=for-the-badge)](https://github.com/NvxStrikes/smart_render_guard)

<br/>

> **Stop losing hours of render time to preventable Out-Of-Memory crashes, broken animation drivers, and missing textures.**  
> Smart Render Guard analyzes your scene before Blender starts rendering, alerting you to critical bottlenecks and freeing memory with a single click.

<br/>

[✨ Features](#-core-features) • [⚡ Quick Start](#-quick-start) • [📊 Telemetry Preview](#-live-telemetry-preview) • [⚔️ Lite vs Pro](#️-edition-comparison) • [📄 License](#-license)

</div>

---

## ⚡ Live Telemetry Preview

When you trigger a scan in the 3D Viewport sidebar (`N`), Smart Render Guard runs deep hardware and scene diagnostics in milliseconds:

```yaml
==================== [ SMART RENDER GUARD TELEMETRY ] ====================
 🖥️ GPU Hardware   : NVIDIA GeForce RTX 4090 (24,576 MB)
 📊 VRAM Real-Time : [████████████░░░░░░░░] 52.4% (12,877 MB / 24,576 MB)
 🧠 System RAM     : [████████░░░░░░░░░░░░] 38.1% (24,384 MB / 64,000 MB)
 📐 Triangles      : 8,420,110 (L3 Subdivisions flagged on 'Hero_Char')
 🖼️ Textures       : 42 Image Blocks (3,120 MB evaluated memory)
--------------------------------------------------------------------------
 🔍 PRE-RENDER VALIDATION:
   ❌ [CRITICAL] 2 Missing External Texture Paths (Pink Render Risk!)
   ⚠️ [WARNING]  1 Broken Armature Driver Target ('spine_fk_ctrl')
   ✅ [SAFE]     No heavy orphan geometry blocks found
--------------------------------------------------------------------------
 💡 OVERALL SCENE STATUS: [ ⚠️ WARNING ] — Auto-Fix Available
==========================================================================
```

---

## ✨ Core Features

<table>
<tr>
<td width="50%">

### 🔍 Pre-Render Scene Validator
Catches common crash causes *before* you press render:
* **Missing External Textures**: Flags unlinked or relocated image files so you never get a pink texture render.
* **Broken Animation Drivers**: Finds invalid driver targets across meshes, shape keys, and material node trees.
* **Missing Linked Libraries**: Scans linked `.blend` files for missing asset references.
* **Heavy Modifier Stack Alert**: Flags dangerous subdivision levels (L3+) that cause silent memory crashes.

</td>
<td width="50%">

### 🧹 One-Click Memory Purger
Clear garbage and reclaim RAM immediately:
* **Orphan Data Purging**: Recursively eliminates unused materials, orphaned meshes, node groups, and leftover image blocks.
* **Cache Reclaimer**: Cleans out viewport calculation artifacts to prevent RAM/VRAM exhaustion during marathon 3D modeling sessions.
* **Zero-Freeze Execution**: Lightweight and native Python routines optimized for instant responsiveness.

</td>
</tr>
<tr>
<td width="50%">

### 📊 Real-Time Hardware Diagnostics
Always know your exact resource limits:
* **Live VRAM & RAM Telemetry**: Real-time load indicators for your GPU and system memory.
* **Multi-Platform GPU Detection**: Seamless driver queries for NVIDIA, AMD, Intel, and Apple Silicon.
* **Scene Memory Breakdown**: Instant tally of evaluated polygon density, active materials, and texture memory load.

</td>
<td width="50%">

### 🎬 Safe Render Workflow
Built-in safeguard for your renders:
* **Pre-Render Interceptor**: Automatically warns you if your scene exceeds safe memory thresholds before rendering.
* **One-Click Safe Fixes**: Automatically dial back viewport and render subdivision spikes safely with full undo (`Ctrl + Z`) support.

</td>
</tr>
</table>

---

## ⚡ Quick Start

<details open>
<summary><b>Installation via ZIP (Recommended)</b></summary>

1. Click **Code > Download ZIP** (or grab a release package).
2. Open Blender, navigate to:
   ```
   Edit > Preferences > Add-ons
   ```
3. Click the **Install...** button in the top corner (or the dropdown arrow in Blender 4.2+).
4. Select the `.zip` archive and click **Install Add-on**.
5. Enable the checkbox for **Smart Render Guard Lite**.
</details>

<details>
<summary><b>Direct Folder Installation (Power Users)</b></summary>

Clone or copy the `smart_render_guard` folder directly into your Blender addons directory:

* **Windows**:
  ```bash
  %APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\smart_render_guard
  ```
* **macOS**:
  ```bash
  ~/Library/Application Support/Blender/<version>/scripts/addons/smart_render_guard
  ```
* **Linux**:
  ```bash
  ~/.config/blender/<version>/scripts/addons/smart_render_guard
  ```

Restart Blender or click **Refresh** in Preferences > Add-ons, then enable the addon.
</details>

---

## 🚀 How To Use

1. **Open the Sidebar**: In Blender's 3D Viewport, press **`N`** to expand the side shelf.
2. **Select the Tab**: Click the **Render Guard** tab.
3. **Run a Scan**: Click **`🔍 SCAN SCENE`** to see instant memory load, triangle count, and risk diagnostics.
4. **Validate Scene**: Check the **Pre-Render Validation** section to see if textures or drivers are broken.
5. **Optimize**: Click **`⚡ AUTO-FIX SAFE ISSUES`** to lower dangerous subdivisions, or **`Purge Memory Cache`** to reclaim RAM.
6. **Render Safely**: Click **`🎬 SAFE RENDER`** to ensure clean, crash-free output!

---

## ⚔️ Edition Comparison

Smart Render Guard is available in a free open-source **Lite** edition and a high-performance **Pro** edition for production studios and power artists.

> [!NOTE]
> *Looking for the Basic edition? Basic has been discontinued so that all advanced features are concentrated directly into **Smart Render Guard Pro**.*

| Feature | Lite (Free & Open Source) | Pro (Studio Edition) |
| :--- | :---: | :---: |
| **Real-Time RAM & VRAM Diagnostics** | ✅ | ✅ |
| **Pre-Render Scene & Asset Validation** | ✅ | ✅ |
| **Broken Animation Driver Detection** | ✅ | ✅ |
| **Missing Texture & File Scanner** | ✅ | ✅ |
| **One-Click Memory Cache Purger** | ✅ | ✅ |
| **Automatic Subdivision Reducer** | ✅ | ✅ |
| **Safe Render Mode (Pre-Flight Check)** | ✅ | ✅ |
| **Automated Geometry Instancer** *(Link Duplicates)* | ❌ | 💎 **Included** |
| **Non-Destructive Texture Downscaler** *(128px–8K)* | ❌ | 💎 **Included** |
| **Missing Texture Locate & Relink Helper** | ❌ | 💎 **Included** |
| **Cycles Light Path Throttler** *(Bounce Clamping)* | ❌ | 💎 **Included** |
| **Automatic Scene Safety Backup** *(Auto-Restore)* | ❌ | 💎 **Included** |
| **One-Click Shader Graph Simplifier & Restorer** | ❌ | 💎 **Included** |
| **Black Box Crash Forensics Logger** | ❌ | 💎 **Included** |
| **Unattended Background CLI Autopilot** | ❌ | 💎 **Included** |

<div align="center">

Ready for studio-grade batch optimization, automated texture downscaling, and crash forensics?  
👉 **[Upgrade to Smart Render Guard Pro at novastrikes.com](https://novastrikes.com)**

</div>

---

## 📄 License

Smart Render Guard Lite is proudly free and open-source software distributed under the terms of the **GNU General Public License v3.0 (GPL-3.0)**.  
See the [LICENSE](LICENSE) file for complete terms and rights.

<div align="center">
<sub>Engineered with precision for 3D Artists, Animators, and Technical Directors.</sub>
</div>
