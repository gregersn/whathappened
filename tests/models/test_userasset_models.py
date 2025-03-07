from pathlib import Path

from whathappened.core.userassets.models import Asset, AssetFolder
from whathappened.web.userassets.utils import resolve_system_path


valid_asset_folder = AssetFolder(owner_id=1, title="Foolder")
sub_folder = AssetFolder(owner_id=1, title="Subfolder")


def test_valid_folder(new_session):
    new_session.add(valid_asset_folder)
    new_session.commit()

    foolder = new_session.query(AssetFolder).filter_by(title="Foolder").first()

    assert foolder.title == "Foolder"
    assert foolder.owner_id == 1

    assert (
        foolder.get_path() == Path(str(foolder.id)) / foolder.title
    ), foolder.get_path()

    assert foolder.path == Path(foolder.title), foolder.path

    assert (
        resolve_system_path(foolder)
        == Path("uploads") / str(foolder.id) / foolder.title
    ), resolve_system_path(foolder)

    new_session.rollback()


def test_sub_folder(new_session):
    new_session.add(valid_asset_folder)
    new_session.commit()

    foolder = new_session.query(AssetFolder).first()

    sub_folder.parent_id = foolder.id

    new_session.add(sub_folder)
    new_session.commit()

    sub_foolder = new_session.query(AssetFolder).filter_by(title="Subfolder").first()

    assert sub_foolder
    assert sub_folder.parent_id == foolder.id

    assert (
        sub_folder.get_path()
        == Path(str(foolder.id)) / foolder.title / sub_folder.title
    )

    assert sub_folder.path == Path(foolder.title) / sub_folder.title


def test_asset(new_session):
    # new_session.add(valid_asset_folder)
    # new_session.commit()
    folder = new_session.query(AssetFolder).first()
    asset = Asset(filename="foo.png", owner_id=1, folder_id=folder.id)

    new_session.add(asset)
    new_session.commit()

    new_asset = new_session.query(Asset).first()

    assert new_asset
    assert new_asset.path == folder.get_path() / "foo.png"
    assert resolve_system_path(new_asset) == resolve_system_path(folder) / "foo.png"

    new_session.delete(new_asset)
    new_session.commit()
