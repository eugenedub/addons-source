#------------------------------------------------------------------------
#
# Register the Addon
#
#------------------------------------------------------------------------

register(GENERAL,
         category="WebConnect",
         id="FR Web Connect Pack",
         name=_("FR Web Connect Pack"),
         description = _("Collection of Web sites for the FR (requires libwebconnect)"),
         status = UNSTABLE, # unicode issue with python 3
         version = '1.0.16',
         gramps_target_version = "4.1",
         fname="FRWebPack.py",
         load_on_reg = True,
         depends_on = ["libwebconnect"]
         )

