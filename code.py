
import build
import saber

saber = saber.Saber()

# This works around what would be a circular import
saber.saber_build = build

saber.main()