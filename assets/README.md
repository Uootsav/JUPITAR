# Font assets
The Windows build runs tools/download_font.py to download Rajdhani-SemiBold.ttf
and the original OFL license before packaging. No font binary is in this source
ZIP. The compiled application loads the bundled font privately; end users do not
install it. Body text uses Windows script fallback for Gujarati.
