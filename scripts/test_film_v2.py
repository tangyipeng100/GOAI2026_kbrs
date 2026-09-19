"""Regression checks for complete, proportional video framing."""

import unittest

from PIL import Image

from render_overview_film_v2 import fit_rect, paste_contained, source_index


class FilmFramingTests(unittest.TestCase):
    def test_original_replay_is_pixel_aligned(self):
        self.assertEqual(fit_rect((1920, 852), (0, 96, 1920, 852)), (0, 96, 1920, 852))

    def test_landscape_fits_without_cover_crop(self):
        x, y, w, h = fit_rect((1920, 852), (10, 20, 1110, 1080))
        self.assertEqual(w, 1110)
        self.assertLess(h, 1080)
        self.assertAlmostEqual(w / h, 1920 / 852, places=2)
        self.assertGreaterEqual(x, 10)
        self.assertGreaterEqual(y, 20)

    def test_all_four_source_corners_survive(self):
        source = Image.new("RGB", (1920, 852), "white")
        colors = ("red", "green", "blue", "yellow")
        from PIL import ImageDraw
        draw = ImageDraw.Draw(source)
        for box, color in zip([(0, 0, 15, 15), (1904, 0, 1919, 15), (0, 836, 15, 851), (1904, 836, 1919, 851)], colors):
            draw.rectangle(box, fill=color)
        output = Image.new("RGB", (1920, 1080), "black")
        paste_contained(output, source, (0, 96, 1920, 852))
        for x, y in ((0, 0), (1919, 0), (0, 851), (1919, 851)):
            self.assertEqual(source.getpixel((x, y)), output.getpixel((x, y + 96)))

    def test_end_frame_holds_instead_of_looping(self):
        self.assertEqual(source_index(9, 5, 39), 38)
        self.assertEqual(source_index(0, 5, 39), 0)
        self.assertEqual(source_index(3, 5, 39), 15)


if __name__ == "__main__":
    unittest.main()
