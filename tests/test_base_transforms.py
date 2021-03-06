import solt.transforms as slt
import solt.core as slc
import numpy as np
import pytest
import sys
import inspect
import torch

from .fixtures import *


def get_transforms_solt():
    trfs = []
    for name, obj in inspect.getmembers(sys.modules["solt.transforms"]):
        if inspect.isclass(obj):
            trfs.append(obj)
    return trfs


def class_accepts(obj, parameter):
    return parameter in inspect.signature(obj.__init__).parameters.keys()


def filter_trfs(trfs, parameter):
    return filter(lambda t: class_accepts(t, parameter), trfs)


def filter_trfs_subclass(trfs, superclass):
    return filter(lambda t: issubclass(t, superclass), trfs)


all_trfs_solt = get_transforms_solt()


@pytest.mark.parametrize("trf", filter_trfs(all_trfs_solt, "data_indices"))
def test_data_indices_cant_be_list(trf):
    with pytest.raises(TypeError):
        trf(data_indices=[])


@pytest.mark.parametrize("trf", filter_trfs(all_trfs_solt, "p"))
def test_base_transform_can_take_none_prop_and_it_becomes_0_5(trf):
    assert 0.5 == trf(p=None).p


@pytest.mark.parametrize("trf", filter_trfs(all_trfs_solt, "data_indices"))
def test_data_indices_can_be_only_int(trf):
    with pytest.raises(TypeError):
        trf(data_indices=("2", 34))


@pytest.mark.parametrize("trf", filter_trfs(all_trfs_solt, "data_indices"))
def test_data_indices_can_be_only_nonnegative(trf):
    with pytest.raises(ValueError):
        trf(data_indices=(0, 1, -2))


@pytest.mark.parametrize("img", [img_2x2(), ])
@pytest.mark.parametrize("trf", filter_trfs(all_trfs_solt, "p"))
def test_transform_returns_original_data_if_use_transform_is_false(img, trf):
    dc = slc.DataContainer((img,), "I")
    trf = trf(p=0)
    res = trf(dc)
    np.testing.assert_array_equal(res.data[0], img)


@pytest.mark.parametrize("trf", [slt.Flip, slt.HSV, slt.Brightness])
@pytest.mark.parametrize("img", [img_3x3_rgb(), ])
def test_transform_returns_original_data_if_not_in_specified_indices(trf, img):
    img_3x3 = img * 128
    kpts_data = np.array([[0, 0], [0, 2], [2, 2], [2, 0]]).reshape((4, 2))
    kpts = slc.Keypoints(kpts_data.copy(), frame=(3, 3))
    dc = slc.DataContainer((img_3x3.copy(), img_3x3.copy(), img_3x3.copy(),
                            img_3x3.copy(), 1, kpts, 2), "IIIILPL")

    kwargs = {"p": 1, "data_indices": (0, 1, 4)}
    if class_accepts(trf, "gain_range"):
        kwargs["gain_range"] = (0.7, 0.9)
    if class_accepts(trf, "brightness_range"):
        kwargs["brightness_range"] = (10, 20)
    if class_accepts(trf, "h_range"):
        kwargs["h_range"] = (50, 50)
        kwargs["s_range"] = (50, 50)
    if class_accepts(trf, "h_range"):
        kwargs["h_range"] = (50, 50)
        kwargs["s_range"] = (50, 50)

    trf = trf(**kwargs)
    res = trf(dc)

    assert np.linalg.norm(res.data[0] - img_3x3) > 0
    assert np.linalg.norm(res.data[1] - img_3x3) > 0
    np.testing.assert_array_equal(res.data[2], img_3x3)
    np.testing.assert_array_equal(res.data[3], img_3x3)
    assert res.data[-1] == 2
    np.testing.assert_array_equal(res.data[5].data, kpts_data)


@pytest.mark.parametrize("img_1, img_2", [(img_2x2(), img_6x6()),
                                          (img_3x3(), img_3x4()),])
def test_data_dep_trf_raises_value_error_when_imgs_are_of_different_size(img_1, img_2):
    trf = slt.SaltAndPepper(gain_range=0.0, p=1)
    with pytest.raises(ValueError):
        trf(slc.DataContainer((1, img_1.astype(np.uint8), img_2.astype(np.uint8)), "LII"))


@pytest.mark.parametrize("img", [img_2x2(), ])
def test_transform_returns_original_data_when_not_used_and_applied(img):
    trf = slt.Flip(p=0)
    dc = slc.DataContainer(img, "I")
    dc_res = trf(dc)
    assert dc_res == dc


@pytest.mark.parametrize("data", [[123,], "123", 2.3])
def test_wrap_data_throws_a_type_error_when_unknown_type(data):
    with pytest.raises(TypeError):
        slc.BaseTransform.wrap_data(data)


@pytest.mark.parametrize("data", [img_2x2(), slc.DataContainer(img_2x2(), "I")])
def test_data_container_wraps_correctly(data):
    dc = slc.DataContainer(img_2x2(), "I")
    assert slc.BaseTransform.wrap_data(data) == dc


@pytest.mark.parametrize("img", [img_3x3(), ])
@pytest.mark.parametrize("return_torch", [False, True])
@pytest.mark.parametrize("trf", filter(lambda t: not issubclass(t, slt.HSV), all_trfs_solt))
def test_transforms_return_torch(img, trf, return_torch):
    if "p" in inspect.getfullargspec(trf.__init__):
        trf: slc.BaseTransform = trf(p=1)
    else:
        trf: slc.BaseTransform = trf()
    res = trf({"image": img},
              return_torch=return_torch, as_dict=False,
              mean=(0.5,), std=(0.5,))

    assert isinstance(res, torch.FloatTensor) == return_torch
