def migrate(cr, version):
    """
    Post-migration script
    """
    # Fields are now store=False (computed on-the-fly)
    # No recomputation needed
    pass
