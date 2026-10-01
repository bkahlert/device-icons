<p align="center">
  <img src="docs/public.generic-pc.png" alt="The PC icon Finder draws for a host without a model identifier" height="192">
</p>

# Device Icons [![CI](https://github.com/bkahlert/device-icons/actions/workflows/ci.yml/badge.svg)](https://github.com/bkahlert/device-icons/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/bkahlert/device-icons?color=69B745&label=Release&logo=GitHub&logoColor=fff)](https://github.com/bkahlert/device-icons/releases/latest) [![License](https://img.shields.io/github/license/bkahlert/device-icons?color=29ABE2&label=License)](https://github.com/bkahlert/device-icons/blob/main/LICENSE) [![Buy Me A Coffee](https://img.shields.io/static/v1?label=&message=%E2%98%95%20Buy%20Me%20A%20Coffee&color=FFDD00)](https://www.buymeacoffee.com/bkahlert)

Any host on your network can show up in Finder with the icon of an Apple device. A Raspberry Pi or a NAS will do.

The host announces itself over Bonjour, and its `_device-info._tcp` record carries a `model` value. Finder draws the
icon for that model. For example, `model=MacPro7,1` gives the 2019 Mac Pro tower.

Two commands help you choose a model identifier:

- [`dump`](#dump) writes every icon macOS has for a model identifier and groups them, so you can pick one by eye in
  Finder.
- [`preview`](#preview) shows the icon for a model identifier in Finder's Network view. You don't need the device.

A third, [`symbols`](#symbols), writes the SF Symbol of each device type as SVG, for a project that draws devices
itself.

All three run on macOS only. The icons live in `CoreTypes.bundle`, the symbols in `CoreGlyphs.bundle`, and `iconutil`,
`osascript`, `open`, and `dns-sd` do work that no Python module does. You need [uv](https://docs.astral.sh/uv/); the
tool itself uses only the standard library.

Run the commands from a checkout with `uv run device-icons`, or without a checkout:

```bash
uvx --from git+https://github.com/bkahlert/device-icons device-icons --help
```

Once you have chosen a model identifier, set it as `model=<identifier>` in your host's `_device-info._tcp` record.
[Pi Hero](https://github.com/bkahlert/pihero) does that for a Raspberry Pi.

![Finder's Network view showing the eleven devices of the table below](docs/network-view.png)

<!--
docs/network-view.png: Finder's Network view with the eleven devices of the table below announced by

    uv run device-icons preview --no-open AirPort4 AirPort5 AirPort6 AirPort7,120 Macmini8,1 Macmini9,1 \
      MacPro6,1 MacPro5,1 MacPro7,1@ECOLOR=225,225,223 MacPro7,1@ECOLOR=226,226,224 Xserve3,1

Icon view grouped by Kind, toolbar and sidebar hidden, captured with shift-command-4 on a Retina display, then the
hosts of the home network edited out with ChatGPT Astra, one of them kept as the PC.
-->

## Dump

Here are eleven of the icons, laid out by `dump --horizontal`:

| Model identifier | `AirPort4` | `AirPort5` | `AirPort7,120` | `Macmini8,1` | `Macmini9,1` | `MacPro5,1` | `MacPro6,1` | `AirPort6` | `Xserve3,1` | `MacPro7,1`<br/>`@ECOLOR=`<br/>`225,225,223` | `MacPro7,1`<br/>`@ECOLOR=`<br/>`226,226,224` |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Type identifier | `com.apple.airport-express` | `com.apple.airport` | `com.apple.airport-extreme-tower` | `com.apple.macmini-2018` | `com.apple.macmini-2020` | `com.apple.macpro-firewire` | `com.apple.macpro-cylinder` | `com.apple.time-capsule` | `com.apple.xserve-xeon` | `com.apple.macpro-2019` | `com.apple.macpro-2019-rackmount` |
| Kind | Mac | AirPort Extreme | AirPort Extreme | Mac | Mac | Mac | Mac | Time Capsule | Mac | Mac | Mac |
| Icon | <img src="docs/icons/icons/com.apple.airport-express.png" alt="com.apple.airport-express" width="128"> | <img src="docs/icons/icons/com.apple.airport-extreme.png" alt="com.apple.airport-extreme" width="128"> | <img src="docs/icons/icons/com.apple.airport-extreme-tower.png" alt="com.apple.airport-extreme-tower" width="128"> | <img src="docs/icons/icons/com.apple.macmini-2018.png" alt="com.apple.macmini-2018" width="128"> | <img src="docs/icons/icons/com.apple.macmini-2020.png" alt="com.apple.macmini-2020" width="128"> | <img src="docs/icons/icons/com.apple.macpro.png" alt="com.apple.macpro" width="128"> | <img src="docs/icons/icons/com.apple.macpro-cylinder.png" alt="com.apple.macpro-cylinder" width="128"> | <img src="docs/icons/icons/com.apple.time-capsule.png" alt="com.apple.time-capsule" width="128"> | <img src="docs/icons/icons/com.apple.xserve.png" alt="com.apple.xserve" width="128"> | <img src="docs/icons/icons/com.apple.macpro-2019.png" alt="com.apple.macpro-2019" width="128"> | <img src="docs/icons/icons/com.apple.macpro-2019-rackmount.png" alt="com.apple.macpro-2019-rackmount" width="128"> |
| Sidebar icon | <img src="docs/icons/sidebar/SidebarAirportExpress.png" alt="SidebarAirportExpress" width="32"> | <img src="docs/icons/sidebar/SidebarAirportExtreme.png" alt="SidebarAirportExtreme" width="32"> | <img src="docs/icons/sidebar/SidebarAirportExtremeTower.png" alt="SidebarAirportExtremeTower" width="32"> | <img src="docs/icons/sidebar/SidebarMacMini.png" alt="SidebarMacMini" width="32"> | <img src="docs/icons/sidebar/SidebarMacMini.png" alt="SidebarMacMini" width="32"> | <img src="docs/icons/sidebar/SidebarMacPro.png" alt="SidebarMacPro" width="32"> | <img src="docs/icons/sidebar/SidebarMacProCylinder.png" alt="SidebarMacProCylinder" width="32"> | <img src="docs/icons/sidebar/SidebarTimeCapsule.png" alt="SidebarTimeCapsule" width="32"> | <img src="docs/icons/sidebar/SidebarXserve.png" alt="SidebarXserve" width="32"> | <img src="docs/icons/sidebar/com.apple.macpro-2019.png" alt="com.apple.macpro-2019" width="32"> | <img src="docs/icons/sidebar/com.apple.macpro-2019-rackmount.png" alt="com.apple.macpro-2019-rackmount" width="32"> |

<!--
The table above is docs/icons/README.md, made with

    uv run device-icons dump --horizontal --no-open \
      --model AirPort4 --model AirPort5 --model AirPort6 --model AirPort7,120 \
      --model Macmini8,1 --model Macmini9,1 --model MacPro6,1 --model MacPro5,1 \
      --model MacPro7,1@ECOLOR=225,225,223 --model MacPro7,1@ECOLOR=226,226,224 \
      --model Xserve3,1 \
      docs/icons

then pngquant --ext .png --force docs/icons/icons/*.png to keep the repository small, and the image paths
prefixed with docs/icons/ since this file sits at the repository root.
-->

To get every icon:

```bash
uv run device-icons dump
```

`dump` reads each model identifier declared in `CoreTypes.bundle` and asks LaunchServices which type it resolves to. It
then writes that type's icon and sidebar icon, grouped by sidebar icon:

| Path                              | Content                                                                                                            |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `icons/<icon>.png`                | the largest image of each icon file, written once                                                                  |
| `sidebar/<sidebar>.png`           | each sidebar icon at 64 px, written once; named after its `Sidebar….icns`, or after its icon file when embedded there |
| `by-sidebar/<sidebar>/`           | one folder per sidebar icon, with that sidebar icon as the folder's icon                                           |
| `by-sidebar/<sidebar>/<icon>.png` | a link to `icons/<icon>.png` for every icon that comes with that sidebar icon                                      |
| `index.json`                      | `sidebars` lists each sidebar icon, its icons, and their type and model identifiers; `dropped` lists the model identifiers left out, by reason |
| `README.md`                       | the same data as a table, one row per model identifier: type identifier, Kind, icon, sidebar icon                 |

The dump goes to `out/`, or to the directory you name, and opens in Finder. `dump` creates the directory if needed.

If the directory already holds an earlier dump, `dump` replaces it. Anything else in it makes `dump` stop, so it never
deletes your files. It recognises an earlier dump by its file names and the first line of its `README.md`.

### Pick an icon

Open `by-sidebar/` in Finder. Each folder shows a sidebar icon as its folder icon and holds the icons that come with it.

Once you have picked an icon, look it up in `index.json`. It lists the model identifiers that produce the icon, and any
of them works as `model=…`:

```json
{
  "sidebars": {
    "SidebarXserve": {
      "sidebar_icon": "sidebar/SidebarXserve.png",
      "icons": {
        "com.apple.xserve": {
          "icon": "icons/com.apple.xserve.png",
          "type_identifiers": ["com.apple.xserve", "com.apple.xserve-xeon", "com.apple.mac.rackmount"],
          "model_identifiers": ["RackMac", "RackMac1,1", "Xserve", "Xserve3,1"]
        }
      }
    }
  }
}
```

`dropped`, next to `sidebars`, lists what `dump` left out and why. Displays are left out because their types are no
devices. Apple TV, Watch, and AirPods are left out because their types have no sidebar icon.

Check the result with [`preview`](#preview).

### Dump a few

To dump only your project's devices into its docs, without opening Finder:

```bash
uv run device-icons dump --no-open --model MacPro7,1 --model Xserve3,1 docs/icons
```

To dump whole types instead:

```bash
uv run device-icons dump --no-open --type com.apple.macpro-2019 --type com.apple.xserve-xeon docs/icons
```

`--model` takes the model identifiers you name and the types they resolve to. `--type` takes the type identifiers you
name and the model identifiers that resolve to them. You can't combine the two.

`dump` stops before it writes anything if an identifier is not declared or resolves to no type. It also stops if the
type has no icon or no sidebar icon. The message names the identifier and says what is missing.

### A table for a README

`--horizontal` turns the table in `README.md` on its side. It gets one column per model identifier, and one row each
for type identifier, Kind, icon, and sidebar icon. The table at the top of this section was made this way:

```bash
uv run device-icons dump --horizontal --no-open --model MacPro7,1 --model Xserve3,1 docs/icons
```

## Preview

To see the icon Finder draws for a model identifier, without owning the device:

```bash
uv run device-icons preview MacPro7,1
```

Finder's Network view opens. Within a few seconds a device named `MacPro7,1` appears, with the icon that identifier
produces, as pictured above.

`preview` keeps the device there until you press Ctrl-C, it receives a termination signal, or one of its registrations
ends. Then it unregisters.

To compare several at once:

```bash
uv run device-icons preview MacPro7,1 Xserve3,1 "Mac14,8@ECOLOR=1"
```

To use the name your real device will have, pass `--name`. It takes one model identifier at a time, because Finder pairs
a device's records by name:

```bash
uv run device-icons preview --name "Rack" MacPro7,1@ECOLOR=226,226,224
```

`--no-open` doesn't open Finder. Open the Network view yourself with Go > Network or ⇧⌘K.

`preview` can't show the sidebar icon. Finder shows it only under Locations, for a server it has mounted, and the
previewed host does not exist.

## Symbols

To write the SF Symbol of every device type as SVG:

```bash
uv run device-icons symbols
```

`symbols` resolves each model identifier declared in `CoreTypes.bundle` to its type, as `dump` does, takes the type's
symbol name, and reads the symbol from `CoreGlyphs.bundle` through CoreUI, the framework Finder draws it with. It
writes:

| Path                        | Content                                                                                                                                               |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `symbols/<symbol name>.svg` | the symbol at regular weight and medium scale, written once: a tight `viewBox`, a `path` filled with `currentColor` per layer, no `width` or `height` |
| `index.json`                | `symbols` lists each symbol name, its file, and the type and model identifiers that get it; `dropped` lists the model identifiers left out, by reason |
| `README.md`                 | the same data as a table, one row per model identifier: type identifier, symbol name, symbol                                                          |

The output goes to `out/`, or to the directory you name, and opens in Finder. An earlier run in that directory is
replaced; anything else in it makes `symbols` stop, as with `dump`.

A type without a symbol name takes the one of the nearest type it conforms to, the way it takes an icon file. Whether
Finder inherits symbol names the same way is not verified. Most model identifiers get a symbol this way; the Power Macs
and Xserves are among those that don't. A legacy symbol name such as `visionpro` is followed to its current name,
`vision.pro`, through the bundle's `name_aliases.strings`, as `NSImage` does; the file keeps the name the type declares.
`dropped` names the model identifiers left out: `no type` for one no type declares, `no symbol name` for one whose type
neither declares nor inherits a symbol name, and `no symbol` for one whose symbol name `CoreGlyphs.bundle` doesn't
have, which happens for a private name or two.

A symbol is drawn in its preferred rendering mode, as `NSImage` draws it by default: hierarchical for most device
symbols, monochrome for the Mac Pro and the Apple TV. Hierarchical gives each layer the opacity of its level, 1 for
primary, 0.5 for secondary, 0.3 for tertiary, so the screen of an iPad is a translucent layer under its frame;
monochrome draws every layer at 1. These are AppKit's values; the SF Symbols app's Copy Image as SVG draws tertiary at
0.25. An eraser layer, which the AirPods Pro use to cut the bud behind the ear tip, becomes a `mask` over what is
drawn before it, with the id `eraser-<symbol name>-<layer index>`.

All SVGs share one unit, so the `viewBox` carries each symbol's size relative to the others: the Mac Pro is 101 by 123,
the iPhone 63 by 103. Render them at a common scale to keep that, or let each fill its box.

```json
{
  "symbols": {
    "macpro.gen3": {
      "symbol": "symbols/macpro.gen3.svg",
      "type_identifiers": ["com.apple.macpro", "com.apple.macpro-2019", "com.apple.macpro-2023"],
      "model_identifiers": ["Mac14,8", "Mac14,8@ECOLOR=0", "MacPro", "MacPro7,1", "MacPro7,1@ECOLOR=225,225,223"]
    }
  }
}
```

### A few symbols

`--symbol` takes symbol names, any SF Symbol, declared by a device type or not:

```bash
uv run device-icons symbols --no-open --symbol macpro.gen3 --symbol xserve.raid docs/symbols
```

A symbol no model identifier gets still has its row, with the identifier cells empty, so you can look at it.
`--horizontal` turns the table on its side as it does for `dump`.

`--symbol` matches the name a type declares. Give a renamed symbol by that legacy name, `visionpro` rather than
`vision.pro`, as `index.json` lists it; under its current name it gets its file, but no model identifiers.

`symbols` stops before it writes anything if a symbol name is not in `CoreGlyphs.bundle`. The message names it.

To fetch fresh symbols into another project without a checkout:

```bash
uvx --from git+https://github.com/bkahlert/device-icons device-icons symbols --no-open path/to/symbols
```

The symbols are Apple's; see [License](#license) for what their agreement allows.

## Development

Install the dependencies:

```bash
uv sync
```

Run the tests:

```bash
uv run pytest
```

Lint and format, as CI does:

```bash
uv run ruff check && uv run ruff format --check
```

Run the tool from the checkout:

```bash
uv run device-icons --help
```

CI runs the tests and ruff on macOS 15 and macOS 26. It runs on every push and pull request, and every Monday. The
Monday run catches a macOS update that moves an icon in `CoreTypes.bundle` or changes CoreUI, the private framework
`symbols` reads symbols through, without waiting for a push. `main` only accepts pull requests with green checks.

The package is in `src/device_icons/`, the tests in `tests/`. Logic that needs no macOS, such as reading type
declarations and building the index, is tested on fixtures. The tests replace `dns-sd` and `open` with fakes. Code that
calls `iconutil`, `osascript`, or CoreUI is tested on macOS only.

### Icon lookup

This is how Finder turns a model identifier into an icon. `dump` does the same.

- A model identifier is a tag of the tag class `com.apple.device-model-code`. It sits in a type declaration of
  `CoreTypes.bundle` or of a bundle nested in its `Contents/Library`, such as `MobileDevices.bundle`.
- Several types claim about half the model identifiers, mostly colour variants of one device. LaunchServices picks the
  winner. `dump` asks the way Finder does, for the preferred type identifier of the tag that conforms to
  `public.device`.
- If no type claims a model identifier, it resolves to a dynamic `dyn.*` type and Finder shows a question mark. The
  same happens for a display, because its type conforms to `public.display`, not `public.device`. That is why
  `AppleDisplay2,1` and `AppleDisplay18,2` are the "no type" rows of a full dump.
- A type's icon is its icon file. A type without one inherits the icon file of the nearest parent along
  `UTTypeConformsTo`.
- The sidebar icon comes from one of two places. The first is the `Sidebar….icns` file a type names in
  `_UTTypeTemplateIconFile`. The second is the `sbtp` chunk that newer icon files embed, which `iconutil` unpacks as
  `template_…` images. `dump` prefers the embedded one. Which one Finder prefers when a type has both is not verified.
- A type's symbol is the SF Symbol its symbol name, `UTTypeSymbolName`, names. It lives in `CoreGlyphs.bundle`, in
  nine weights and three scales, and Finder draws it through CoreUI. `symbols` asks CoreUI for regular weight and
  medium scale, and lets a type without a symbol name inherit its nearest parent's, as it does for icon files. Whether
  Finder inherits symbol names is not verified. CoreUI knows a symbol by its current name only; `CoreGlyphs.bundle`
  maps legacy names to current ones in `name_aliases.strings`, and `symbols` follows that map as `NSImage` does. A
  symbol's `CGPath` in CoreUI concatenates its monochrome layers, erasers included, and loses the levels; `symbols`
  reads the layers of the preferred rendering mode one by one instead.
- Finder's Network view draws the icon. The sidebar icon appears only under Locations, for a server that is mounted.

`preview` works the other end of this. For each model identifier it registers two proxy records from your Mac: an
`_smb._tcp` service, and a `_device-info._tcp` service with `model=<identifier>`. Both use the same service instance
name, which defaults to the identifier. Finder pairs them by that name and draws the icon for the model.

### Glossary

These are Apple's terms, checked against the keys in `Info.plist`, the tools' manuals, and the tools' output. Code and
output use them as written here, or in the short form given. Where the language needs it, they are written in
snake_case.

| Term                      | Example                                    | Meaning                                                                                                                                                                                                                                                                                        |
| ------------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model identifier          | `MacPro7,1`                                | The name About This Mac shows and `sysctl hw.model` prints. In `CoreTypes.bundle` it is a tag of the tag class `com.apple.device-model-code`. In a `_device-info._tcp` TXT record it is the value of `model`. It may carry an enclosure colour: `MacPro7,1@ECOLOR=226,226,224`.                 |
| Board name                | `J120AP`                                   | The name `sysctl hw.target` prints. `MobileDevices.bundle` declares board names as model identifiers of iPhones and iPads, and LaunchServices resolves them like any other tag.                                                                                                                |
| Type identifier           | `com.apple.macpro-2019`                    | A Uniform Type Identifier, the `UTTypeIdentifier` of a type declaration. It is case-insensitive. LaunchServices returns `com.apple.ipad-pro-a1670-1` for the declared `com.apple.ipad-pro-A1670-1`. Short form: type.                                                                           |
| Type declaration          |                                            | One entry of `UTExportedTypeDeclarations` in a bundle's `Info.plist`.                                                                                                                                                                                                                          |
| Tag class, tag            | `com.apple.device-model-code`, `MacPro7,1` | `UTTypeTagSpecification` maps tag classes to the tags a type claims. Other tag classes are `public.filename-extension` and `public.mime-type`.                                                                                                                                               |
| Conforms to               | `com.apple.macpro`, `com.apple.mac.tower`  | `UTTypeConformsTo` names the parent types. A type without an icon, sidebar icon, or Kind of its own takes them from the nearest parent.                                                                                                                                                       |
| Preferred type identifier | `com.apple.macpro-2019` for `MacPro7,1`    | The one type identifier LaunchServices returns for a tag that several declarations claim, via `UTTypeCreatePreferredIdentifierForTag`. An unclaimed tag gets a dynamic type, `dyn.…`.                                                                                                          |
| Bundle, bundle identifier | `CoreTypes.bundle`, `com.apple.coretypes`  | A bundle is the directory; its `CFBundleIdentifier` is the bundle identifier. Device types live in `/System/Library/CoreServices/CoreTypes.bundle` and in the bundles nested in its `Contents/Library`.                                                                                        |
| Kind                      | `Mac`, `iPad`, `Time Capsule`              | Finder's Kind column in the Network view. It shows iPhone, iPad, iPod, AirPort Extreme, or Time Capsule for a type that is or conforms to `com.apple.iphone`, `.ipad`, `.ipod`, `.airport`, or `.time-capsule`. It shows Mac for every other model, Apple TV and Watch included, and PC for a host without one. Observed, not documented. |
| Icon                      | `com.apple.macpro-2019.icns`               | The picture Finder draws for a type. It comes from the type's icon file, `UTTypeIconFile`, an `.icns` in the bundle's `Contents/Resources` that holds it at several sizes.                                                                                                                    |
| Sidebar icon              | `SidebarMacPro.icns`                       | The monochrome icon Finder's sidebar draws under Locations. It is either the `Sidebar….icns` file a type names in `_UTTypeTemplateIconFile`, or the `sbtp` chunk embedded in its icon file. Short form: sidebar.                                                                                |
| Template image            | `template_32x32@2x.png`                    | A monochrome image the system tints. AppKit calls this `isTemplate`. It describes how a sidebar icon is rendered, not what it is. `iconutil` names an embedded sidebar icon's images `template_…`.                                                                                             |
| Iconset                   | `icon_512x512@2x.png`                      | The folder `iconutil -c iconset` unpacks an icon file into: one PNG per image, named by point size and scale.                                                                                                                                                                                  |
| Symbol name               | `macpro.gen3`                              | `UTTypeSymbolName`, the SF Symbol of a type. 55 of the 972 device types declare one; `symbols` lets the others inherit the nearest parent's. Some are legacy names, which `name_aliases.strings` maps to current ones.                                                                         |
| Symbol                    | `symbols/macpro.gen3.svg`                  | An SF Symbol: the layered vector shape `CoreGlyphs.bundle` holds under a symbol name. `symbols` writes it as SVG in its preferred rendering mode, a `path` filled with `currentColor` per layer in a tight `viewBox`.                                                                          |
| Layer                     | `hierarchical-1:tertiary`                  | One of the shapes a symbol is drawn from, in order. In hierarchical rendering a layer has a level, primary, secondary, or tertiary, that sets its opacity. An eraser layer erases what the layers before it drew instead of drawing; `symbols` writes it as a `mask`.                          |
| Rendering mode            | hierarchical                               | How a symbol's layers are colored. Monochrome draws every layer in one color; hierarchical draws each in that color at its level's opacity, 1, 0.5, or 0.3. Each symbol prefers one mode, which `NSImage` uses by default and `symbols` always. Multicolor and palette are not written.        |
| Weight, scale             | regular, medium                            | SF Symbols terms. The nine weights run from ultralight to black, as font weights do. The three scales, small, medium and large, size a symbol next to text of one point size. Finder's defaults are regular and medium.                                                                        |
| Asset catalog             | `Assets.car`                               | The compiled catalog CoreUI reads. `CoreGlyphs.bundle` keeps the symbols in `Contents/Resources/Assets.car`, next to `CoreTypes.bundle` in `/System/Library/CoreServices`.                                                                                                                      |
| Service type              | `_device-info._tcp`, `_smb._tcp`           | A DNS-SD service type (RFC 6763). Finder reads `model` from `_device-info._tcp`.                                                                                                                                                                                                               |
| Service instance name     | `MacPro7,1` in `dns-sd -P MacPro7,1 …`     | The name of one instance of a service type. Finder pairs the `_device-info._tcp` record with the `_smb._tcp` record by it.                                                                                                                                                                     |
| TXT record                | `model=MacPro7,1`                          | The key-value pairs of a service instance.                                                                                                                                                                                                                                                     |
| Proxy registration        | `dns-sd -P`                                | Registering a service on behalf of another host, with its host name and address.                                                                                                                                                                                                               |
| Network view              | Go > Network, ⇧⌘K                          | Finder's list of the servers on the local network. `open` on the `Network.app` inside `Finder.app/Contents/Applications` shows it. The `/Network` folder of earlier macOS is gone.                                                                                                             |

### Release

Bump the version on a branch:

```bash
uv version --bump minor
```

Merge it like any other change, then tag `main`:

```bash
git tag v0.2.0 main && git push origin v0.2.0
```

The tag must match the version in `pyproject.toml`. CI then tests the code, builds the wheel and the source
distribution, and publishes them as a [GitHub release](https://github.com/bkahlert/device-icons/releases) with generated
notes. A version with a pre-release marker, such as `0.2.0rc1`, becomes a pre-release.

## Contributing

Star the project or raise issues. A [PayPal donation](https://www.paypal.me/bkahlert) helps too.

## License

MIT covers the code. See [LICENSE](LICENSE).

The icons and symbols the tool writes are Apple's. This project exists for educational purposes: it shows how Finder
turns a model identifier into an icon or a symbol. Apple licenses its system-provided images, SF Symbols included,
solely for developing applications for Apple-branded products, and forbids their use in app icons, logos, or as
trademarks; see section 2.10, *System-Provided Images*, of the
[Xcode and Apple SDKs Agreement](https://www.apple.com/legal/sla/docs/xcode.pdf). Using the images on other platforms
is not allowed under that agreement.
