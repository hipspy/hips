# Licensed under a 3-clause BSD style license - see LICENSE.rst

def healpix_to_hips_tile(hpx_data, tile_width, tile_idx, file_format) -> HipsTile:
    """Create hips tile from healpix data
    
    
    Parameters
    ----------
    hpx_data : np.ndarray
        Healpix data.
    tile_width : int
        Tile width
    tile_idx : int
        Tile index.
    file_format : str
        File format.
    
    Returns
    -------
    hips_tile : `HipsTile`
        Hips tile object.
    
    """
    # shift order
    shift_order = int(np.log2(tile_width))
    hpx_ipix = hips_tile_healpix_ipix_array(shift_order=shift_order)
    offset_ipix = tile_idx * tile_width ** 2
    
    ipix = hpx_ipix + offset_ipix
    tile_data = hpx_data[ipix]
    
    # np.rot90 returns a rotated view so we make a copy here
    # as the view is lost when going through fits io
    tile_data = np.rot90(tile_data).copy()
    
    hpx_order = int(np.log2(hp.npix2nside(hpx_data.size / tile_width ** 2)))
    
    hips_tile_meta = HipsTileMeta(order=hpx_order, ipix=tile_idx, width=tile_width, file_format=file_format)
    hips_tile = HipsTile.from_numpy(hips_tile_meta, tile_data)
    return hips_tile
    

def healpix_to_hips(hpx_data, tile_width, base_path, file_format='fits'):
    """
    Convert healpix image to hips.

    Parameters
    ----------
    hpx_data : np.ndarray
        Healpix data.
    
    """

    n_tiles = hpx_data.size // tile_width ** 2
    for tile_idx in range(n_tiles): 
        tile = healpix_to_hips_tile(hpx_data=hpx_data, tile_width=tile_width,
                                    tile_idx=tile_idx, file_format=file_format)

        filename = base_path / tile.meta.tile_default_path
        filename.parent.mkdir(exist_ok=True, parents=True)
        tile.write(filename=filename)
    
    # Write a minimal property
    properties = f"""
    hips_tile_format = {file_format}
    hips_tile_width = {tile_width}
    hips_frame = galactic
    """
    
    with (base_path / 'properties').open('w') as f:
        f.write(properties)