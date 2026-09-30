# device-icons

Finder draws a network device with the icon of the Apple device its `_device-info._tcp` record names: `model=MacPro7,1`
gives the 2019 Mac Pro tower. This tool dumps every icon macOS knows for such a model identifier, grouped so one can be
picked by eye in Finder, and previews a model identifier in Finder's Network view without owning the device.

macOS only: the icons live in `CoreTypes.bundle`, and `iconutil`, `osascript`, `open`, and `dns-sd` do the work no
Python module does. Needs [uv](https://docs.astral.sh/uv/); the runtime is the standard library.

## Dump

```bash
uv run device-icons dump                                        # into out/
uv run device-icons dump ~/Desktop/device-icons
uv run device-icons dump --type com.apple.macpro-2019 --type com.apple.xserve-xeon docs/icons
uv run device-icons dump --no-open
```

`dump` reads every model identifier declared in `CoreTypes.bundle`, asks LaunchServices which type each resolves to, takes
that type's icon and sidebar icon, and writes:

| Path                             | Content                                                                             |
| -------------------------------- | ----------------------------------------------------------------------------------- |
| `icons/<icon file>.png`          | the largest image of each icon file, written once                                   |
| `sidebar/<sidebar>.png`          | each 64 px sidebar icon, written once, named after its `Sidebar….icns` or, when embedded, after its icon file |
| `by-sidebar/<sidebar>/`          | one folder per sidebar icon, wearing it as its folder icon                          |
| `by-sidebar/<sidebar>/<icon>.png` | a link to `icons/<icon>.png` for every icon that comes with that sidebar icon      |
| `index.json`                     | `sidebars`: sidebar icon, then icon, then types and model identifiers; `dropped`: model identifiers left out, by reason |

`--type` restricts the dump to the given type identifiers and the model identifiers that resolve to them; the layout stays
the same. A type identifier that is not declared, or whose type has no icon or no sidebar icon, ends `dump` with a message
naming it before anything is written.

Open `out/by-sidebar` in Finder: each folder shows a sidebar icon, inside it the realistic icons that go with it. Having
chosen an icon, its model identifiers are in `index.json`:

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
  },
  "dropped": {
    "no type": ["AppleDisplay18,2", "J120AP"],
    "no icon": [],
    "no sidebar icon": ["AirPods1,1", "AppleTV1,1", "Watch8,2"]
  }
}
```

The output directory is emptied first, but only when it is missing, empty, or holds an earlier dump. Once written, it
opens in Finder; `--no-open` skips that.

From another project, without a checkout:

```bash
uvx --from git+https://github.com/bkahlert/device-icons device-icons dump --no-open --type com.apple.macpro-2019 out/
```

## Preview

```bash
uv run device-icons preview MacPro7,1
uv run device-icons preview MacPro7,1 Xserve3,1 "Mac14,8@ECOLOR=1"
uv run device-icons preview --name "Rack" MacPro7,1@ECOLOR=226,226,224
```

`preview` registers, for each model identifier, two proxy records from the Mac itself: an `_smb._tcp` service and a
`_device-info._tcp` service carrying `model=<identifier>`, both under the same service instance name, which defaults to the
identifier. Since Finder pairs the two records by that name, `--name` takes exactly one model identifier. Finder's
Network view opens, unless `--no-open`; the device appears there within a few seconds, drawn with the icon the identifier
produces. `preview` blocks until Ctrl-C, a termination signal, or one of the registrations ending, then unregisters.

The sidebar icon cannot be previewed this way. Finder shows it only under Locations, for a server it has mounted, and
the previewed host does not exist.

## How Finder gets from a model identifier to an icon

- The model identifier is a tag of the tag class `com.apple.device-model-code` in a type declaration of `CoreTypes.bundle`
  or one of the bundles nested in its `Contents/Library`, such as `MobileDevices.bundle`.
- Model identifiers are not unique: about half are claimed by several type declarations, mostly colour variants of one
  device. LaunchServices settles which type wins, and Finder asks it the same way `dump` does: the preferred type
  identifier for the tag, conforming to `public.device`. A model identifier nobody claims resolves to a dynamic `dyn.*`
  type, and Finder shows a question mark.
- A type's icon is its icon file; a type without one inherits the nearest along `UTTypeConformsTo`. The sidebar icon
  comes from one of two places: the `Sidebar….icns` a type names as `_UTTypeTemplateIconFile`, or the `sbtp` chunk
  newer icon files embed, which `iconutil` unpacks as `template_…` images. `dump` prefers the embedded one; which one
  Finder prefers when a type has both is not verified.
- Finder's Network view draws the icon. The sidebar icon appears only under Locations, for a server that is mounted.

## Glossary

The terms are Apple's, verified against the keys in `Info.plist`, the tools' manuals, and what the tools print. Code and
output use them as written here, or the short form given, as snake_case where the language wants it.

| Term                      | Example                                | Meaning                                                                                                                                                                                                                                              |
| ------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model identifier          | `MacPro7,1`                            | What About This Mac shows and `sysctl hw.model` prints. In `CoreTypes.bundle` a tag of the tag class `com.apple.device-model-code`; in a `_device-info._tcp` TXT record the value of `model`. May carry an enclosure colour: `MacPro7,1@ECOLOR=226,226,224`. |
| Board name                | `J120AP`                               | What `sysctl hw.target` prints. `MobileDevices.bundle` declares board names as model identifiers of iPhones and iPads; LaunchServices does not resolve them.                                                                                      |
| Type identifier           | `com.apple.macpro-2019`                | A Uniform Type Identifier (UTI), the `UTTypeIdentifier` of a type declaration. Reverse-DNS like a bundle identifier, but a different thing. Short form: type.                                                                                         |
| Type declaration          |                                        | One entry of `UTExportedTypeDeclarations` in a bundle's `Info.plist`.                                                                                                                                                                                  |
| Tag class, tag            | `com.apple.device-model-code`, `MacPro7,1` | `UTTypeTagSpecification` maps tag classes to the tags a type claims. Other tag classes are `public.filename-extension` and `public.mime-type`.                                                                                                     |
| Conforms to               | `com.apple.macpro`, `com.apple.mac.tower` | `UTTypeConformsTo`: the parent types. A missing icon or sidebar icon is inherited from the nearest parent that has one.                                                                                                                                |
| Preferred type identifier | `com.apple.macpro-2019` for `MacPro7,1` | The one type identifier LaunchServices returns for a tag several declarations claim, via `UTTypeCreatePreferredIdentifierForTag`. An unclaimed tag gets a dynamic type, `dyn.…`.                                                                     |
| Bundle, bundle identifier | `CoreTypes.bundle`, `com.apple.coretypes` | A bundle is the directory; its `CFBundleIdentifier` is the bundle identifier. Device types live in `/System/Library/CoreServices/CoreTypes.bundle` and the bundles nested in its `Contents/Library`.                                                |
| Icon                      | `com.apple.macpro-2019.icns`           | The picture Finder draws for a type. Its icon file, `UTTypeIconFile`, is an `.icns` in the bundle's `Contents/Resources` holding it at several sizes.                                                                                                |
| Sidebar icon              | `SidebarMacPro.icns`                   | The monochrome icon Finder's sidebar draws under Locations, at 16, 18, 24, and 32 pt, with a selected variant. Comes as the `Sidebar….icns` a type names in `_UTTypeTemplateIconFile`, or embedded in an icon file as its `sbtp` chunk. Short form: sidebar. |
| Template image            | `sbtp`, `template_32x32@2x.png`        | A monochrome image the system tints, `isTemplate` in AppKit. How a sidebar icon is rendered, not what it is. `iconutil` names embedded sidebar images `template_…`, the selected variant `template_[selected]…`; the icns chunk codes are `icsb` and `sb24` for the sidebar sizes, `sbtp` for an embedded sidebar icon, `slct` for its selected variant. |
| Iconset                   | `icon_512x512@2x.png`, `template_32x32@2x.png` | The folder `iconutil -c iconset` unpacks an icon file into, one PNG per image, named by point size and scale.                                                                                                                                    |
| Symbol name               | `macpro.gen3`                          | `UTTypeSymbolName`: the SF Symbol of the type. 55 of the 972 device types declare one.                                                                                                                                                                 |
| Service type              | `_device-info._tcp`, `_smb._tcp`       | DNS-SD (RFC 6763). `_device-info._tcp` is the one Finder reads `model` from.                                                                                                                                                                          |
| Service instance name     | `MacPro7,1` in `dns-sd -P MacPro7,1 …` | The name of one instance of a service type. Finder pairs the `_device-info._tcp` record with the `_smb._tcp` record by it.                                                                                                                             |
| TXT record                | `model=MacPro7,1`                      | The key-value pairs of a service instance.                                                                                                                                                                                                             |
| Proxy registration        | `dns-sd -P`                            | Registering a service on behalf of another host, with its host name and address.                                                                                                                                                                       |
| Network view              | Go > Network, ⇧⌘K                      | Finder's list of the servers found on the local network. `open` on the `Network.app` inside `Finder.app/Contents/Applications` shows it; the `/Network` folder of earlier macOS is gone.                                                              |

## Not yet

- SF Symbols: 55 device types name their SF Symbol in `UTTypeSymbolName`. A later `dump` renders these too.
- Checking the sidebar icon in Finder, and which source Finder prefers, needs a host that can be mounted, that is, a real
  device announcing the identifier.

## Development

```bash
uv sync
uv run pytest
uv run device-icons --help
```

Layout: `src/device_icons/` is the package, `tests/` the tests. Logic that needs no macOS, such as reading type
declarations and building the index, is tested on fixtures, and `dns-sd` and `open` are stood in for by fakes; the
parts that call `iconutil` or `osascript` are tested on macOS only.

## Contributing

Star the project or raise issues. A [PayPal donation](https://www.paypal.me/bkahlert) helps too.

## License

MIT. See [LICENSE](LICENSE).
