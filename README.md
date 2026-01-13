# Wankel Engine Generator for Blender

A procedural, Geometry Nodes-based Blender addon that generates a customizable **Wankel (Rotary) Engine** assembly. This tool creates both the epitrochoid housing and the inner rotor


## 🚀 Features
- **Procedural Housing:** Generates a epitrochoid inner chamber based on radius and eccentricity.
- **Dynamic Rotor:** Creates a rotor with #-apexs (standard 3-apex) with adjustable face bulge and apex sharpness
- **Rotor Position:** A single "Shaft Rotation" slider controls the orbital motion.
- **Apex Grooves:** Includes simple adjustable slots on the rotor faces
- **Customizable Clearances:** Fine-tune the tolerance gap between the rotor and housing

## 🛠 Installation
1. Go to Releases
2. Download the `wankel_generator.zip` file.
3. In Blender, go to **Edit > Preferences > Add-ons**.
4. Click **Install...** and select the `.zip` file.
5. Enable the addon by checking the box next to **Mesh: Wankel Engine Generator**.

## 📖 Usage
1. Open the **Add Menu** (`Shift + A`) in the 3D Viewport.
2. Navigate to **Mesh > Wankel Engine**.
3. Use the **Adjust Last Operation** panel (bottom-left) to tweak the parameters.

      `(Go to Modifiers to apply or re-tweak mesh)`

---

## ⚙️ Parameters Explained

### Rotor & Housing
| Property | Description |
| :--- | :--- |
| **Apex Count** | Number of points on the rotor (Standard Wankel = 3). |
| **Radius** | The base size of the engine chamber. |
| **Eccentricity** | Offset between crankshaft center and rotor center. Determines the "pinch." |
| **Face Bulge** | Adjusts the curvature of the rotor faces. |
| **Clearance** | The physical gap between the rotor apexes and the housing wall. |

### Dimensions & Details
| Property | Description |
| :--- | :--- |
| **Groove Width/Depth** | Controls the inset slots on the rotor faces. |
| **Housing Height** | The thickness of the outer engine block. |
| **Rotor Height** | The thickness of the rotor. |
| **Shaft Rotation** | Drive this value to animate the internal cycle. |



## ⚠️ Technical Note
**Not Engineer Grade:** This addon is intended for artistic visualization and motion graphics. While based on real rotary geometry, it does not include accuracy, porting, cooling jackets, or sealing hardware required for mechanical engineering.

## 📜 License
This project is licensed under the MIT License - feel free to modify and use it for your own projects!
