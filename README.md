# 🛡️ Smart Render Guard Lite

**Free & Open Source Scene Crash Scanner & Memory Optimizer for Blender**

[![Blender Version](https://img.shields.io/badge/Blender-3.6%20%7C%204.x%20%7C%205.x-orange.svg)](https://www.blender.org/)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-brightgreen.svg)]()
[![Edition](https://img.shields.io/badge/Edition-Lite%20(Free)-green.svg)]()

Smart Render Guard Lite is an intelligent diagnostic and scene safety addon for Blender. It helps 3D artists avoid render crashes, identify scene bottlenecks, validate assets before initiating long render jobs, and purge unused memory with a single click.

---

## ✨ Features (Lite Edition)

### 🔍 Pre-Render Scene Validation
Inspects your scene for the most frequent causes of render crashes and render failures:
- **Missing External Textures**: Flags unlinked or broken image file paths before you render.
- **Broken Animation Drivers**: Detects invalid driver targets across objects and material node trees.
- **Missing Linked Libraries**: Verifies linked `.blend` libraries and unresolvable linked assets.
- **High-Risk Modifier Stacks**: Identifies heavy subdivision levels, complex particle settings, and geometry spikes that risk out-of-memory crashes.

### 🧹 Memory Cache Purger
- Automatically cleans unlinked meshes, textures, orphan data blocks, and leftover image cache from Blender memory.
- Reduces memory bloat and prevents RAM/VRAM exhaustion during intensive viewport sessions.

### 📊 Real-Time Hardware & Scene Diagnostics
- **VRAM & RAM Monitoring**: Displays available hardware memory, system RAM load, and GPU specifications.
- **Geometry & Texture Breakdown**: Instant overview of total evaluated triangles and texture memory footprint.
- **Color-Coded Risk Indicators**: Instant visual status (**SAFE**, **WARNING**, or **CRITICAL**) to gauge scene stability.

### 🎬 Safe Render Workflow
- Initiates pre-render safety checks whenever you trigger a render to protect your system from freeze-ups.

---

## 🚀 Installation

### Option A: Install from a ZIP
1. Download or package the `smart_render_guard` folder as a `.zip` archive.
2. In Blender, navigate to **Edit > Preferences > Add-ons**.
3. Click the **Install...** button (or dropdown in Blender 4.2+), choose the zip file, and click **Install Add-on**.
4. Enable the checkbox for **Smart Render Guard Lite**.

### Option B: Direct Folder Installation
Copy the `smart_render_guard` directory directly into your Blender addons folder:
- **Windows**: `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\smart_render_guard`
- **macOS**: `~/Library/Application Support/Blender/<version>/scripts/addons/smart_render_guard`
- **Linux**: `~/.config/blender/<version>/scripts/addons/smart_render_guard`

Restart Blender or click **Refresh** in the Add-ons preference window, then enable the addon.

---

## 📖 Usage Guide

1. Open any Blender scene.
2. In the 3D Viewport, press **`N`** to expand the sidebar panel.
3. Select the **Render Guard** tab.
4. Click **🔍 SCAN SCENE** to evaluate scene complexity, VRAM, and RAM usage.
5. In the **Pre-Render Validation** section, click **Scan Scene Now** to check for missing assets and broken drivers.
6. Click **⚡ AUTO-FIX SAFE ISSUES** or **Purge Memory Cache** to optimize memory immediately.
7. Click **🎬 SAFE RENDER** to validate and execute your render safely.

---

## 🔄 Commercial Editions Comparison

Need deeper automation and automated batch optimization? Compare Smart Render Guard editions:

| Feature | Lite (Free) | Basic | Pro |
| :--- | :---: | :---: | :---: |
| **Real-Time RAM & VRAM Diagnostics** | ✅ | ✅ | ✅ |
| **Pre-Render Asset & Driver Validation** | ✅ | ✅ | ✅ |
| **One-Click Memory Cache Purger** | ✅ | ✅ | ✅ |
| **Automated Geometry Instancing** | ❌ | ✅ | ✅ |
| **Texture Downscaler (128px–4K)** | ❌ | ✅ | ✅ |
| **Cycles Light Path Throttler** | ❌ | ✅ | ✅ |
| **Missing Texture Locate & Relink Helper** | ❌ | ✅ | ✅ |
| **Shader Graph Simplifier & Restorer** | ❌ | ❌ | ✅ |
| **Black Box Crash Forensics Logger** | ❌ | ❌ | ✅ |
| **Unattended CLI Autopilot** | ❌ | ❌ | ✅ |

Visit [novastrikes.com](https://novastrikes.com) for details on Basic and Pro editions.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See the [LICENSE](LICENSE) file for details.
