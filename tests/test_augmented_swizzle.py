
import pytest
from metashade.util.testing import ctx_cls_hg

class TestAugmentedSwizzle:
    @ctx_cls_hg
    def test_augmented_swizzle(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('test_swizzle', sh.Float2)(
                v = sh.Float2, f = sh.Float
            ):
                # Test a.x += b
                sh.v.x += sh.f

                # Test a.xy += b.xy
                # sh.v.xy is Float2, sh.v is Float2.
                # sh.v.xy += sh.v produces vec2 += vec2 which is valid.
                sh.v.xy += sh.v

                sh.return_(sh.v)

    @ctx_cls_hg
    def test_underscore_augmented(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('test_underscore', sh.Float2)(
                v = sh.Float2, f = sh.Float
            ):
                # Test a._ += a (vector += vector)
                sh.v._ += sh.v
                sh.return_(sh.v)
