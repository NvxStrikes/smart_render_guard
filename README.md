# 🛡️ Smart Render Guard — Beta Testing Build

Smart Render Guard is an intelligent diagnostics, safety validation, and render optimization toolkit for Blender.

> [!IMPORTANT]
> **BETA BUILD LIFE-LIMIT NOTICE**
> * **Expiration Date**: This Beta testing build will automatically expire and lock itself on **July 25, 2026** (30 days from compilation).
> * **Distribution Prohibited**: Distributing this Beta build or sharing it outside the authorized testing group is strictly prohibited.
> * **Reverse Engineering**: Reverse engineering, copying, or modifying the source code is strictly prohibited (to the maximum extent permitted under GPL v3 compliance).
> * **Updates**: This is a static Beta build. No new updates, patches, or modifications will be added to this repository or build.

---

## 📝 Submit Your Review & Feedback
Your feedback is extremely important to help us refine the final release. If you encounter any bugs, crashes, performance improvements, or have suggestions, please submit your feedback:
👉 **[Beta Feedback & Review Form](https://forms.gle/v9u5ptPkaWd2V5Qc6)**

You can also submit feedback directly from the Blender UI:
* Go to **Edit > Preferences > Add-ons > Smart Render Guard** and click the **Submit Beta Feedback** button.
* Or use the **Submit Feedback** button directly in the active Viewport N-Panel.

---

## 🚀 How to Install & Test

### Step 1: Download the Addon
Download the compiled ZIP file directly from this repository:
* Download [smart_render_guard_beta.zip](smart_render_guard_beta.zip)

### Step 2: Install in Blender
1. Open Blender.
2. Go to **Edit > Preferences > Add-ons**.
3. Click the **Install...** button in the top right corner.
4. Select the downloaded `smart_render_guard_beta.zip` file and click **Install Add-on**.
5. Enable the addon by checking the box next to **Smart Render Guard Beta**.

### Step 3: Run the Diagnostics
1. Open any heavy Blender scene.
2. In the 3D Viewport, press `N` to open the sidebar and navigate to the **Render Guard** tab.
3. Click **🔍 SCAN SCENE** to run the diagnostics.
4. Review the overall risk status (SAFE, WARNING, or CRITICAL) and the detailed diagnostics (VRAM usage, system RAM, total triangles, and textures).

### Step 4: Validate & Render Safely
1. In the sidebar panel, navigate to the **Pre-Render Validation** section.
2. Click **Scan Scene Now** to check for broken drivers, missing libraries, missing textures, and heavy/unoptimized modifiers.
3. Click **🎬 SAFE RENDER** to perform a final safety validation and run the render.

---

## 💡 Quick Tips for Testing
* **Check the System Consoles**: Press **Window > Toggle System Console** in Blender to view detailed execution logs with the `[SRG]` prefix.
* **Force Expiration Check**: If you want to test what happens when the Beta expires, you can temporarily change your system clock to past July 25, 2026. The addon panels will disable/gray out, and all operator runs and render hooks will safely block.
