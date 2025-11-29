# Meson build file for translations
if meson.is_subproject()
  subdir_done()
endif

i18n = import('i18n')

# Use standard Meson gettext handling which reads LINGUAS automatically if present
# or can be manually specified. The manual LINGUAS reading in the comment
# was a bit complex for a standard meson setup.
# Standard: https://mesonbuild.com/i18n-module.html#gettext

i18n.gettext('aurynk',
  preset: 'glib'
)
