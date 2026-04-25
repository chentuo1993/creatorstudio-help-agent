"""Knowledge-base scope: which Apple Creator Studio apps to ingest, and from where."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppSource:
    name: str
    slug: str
    welcome_urls: tuple[str, ...]
    platforms: tuple[str, ...]


APPS: tuple[AppSource, ...] = (
    AppSource(
        name="Final Cut Pro",
        slug="final-cut-pro",
        welcome_urls=(
            "https://support.apple.com/guide/final-cut-pro/welcome/mac",
            "https://support.apple.com/guide/final-cut-pro-ipad/welcome/ipados",
        ),
        platforms=("mac", "ipad"),
    ),
    AppSource(
        name="Motion",
        slug="motion",
        welcome_urls=("https://support.apple.com/guide/motion/welcome/mac",),
        platforms=("mac",),
    ),
    AppSource(
        name="Compressor",
        slug="compressor",
        welcome_urls=("https://support.apple.com/guide/compressor/welcome/mac",),
        platforms=("mac",),
    ),
    AppSource(
        name="Logic Pro",
        slug="logicpro",
        welcome_urls=(
            "https://support.apple.com/guide/logicpro/welcome/mac",
            "https://support.apple.com/guide/logicpro-ipad/welcome/ipados",
        ),
        platforms=("mac", "ipad"),
    ),
    AppSource(
        name="MainStage",
        slug="mainstage",
        welcome_urls=("https://support.apple.com/guide/mainstage/welcome/mac",),
        platforms=("mac",),
    ),
    AppSource(
        name="Pixelmator Pro",
        slug="pixelmator-pro",
        welcome_urls=("https://support.apple.com/guide/pixelmator-pro/welcome/macos",),
        platforms=("mac",),
    ),
    AppSource(
        name="Keynote",
        slug="keynote",
        welcome_urls=(
            "https://support.apple.com/guide/keynote/welcome/mac",
            "https://support.apple.com/guide/keynote-ipad/welcome/ipados",
            "https://support.apple.com/guide/keynote-iphone/welcome/ios",
        ),
        platforms=("mac", "ipad", "iphone"),
    ),
    AppSource(
        name="Pages",
        slug="pages",
        welcome_urls=(
            "https://support.apple.com/guide/pages/welcome/mac",
            "https://support.apple.com/guide/pages-ipad/welcome/ipados",
            "https://support.apple.com/guide/pages-iphone/welcome/ios",
        ),
        platforms=("mac", "ipad", "iphone"),
    ),
    AppSource(
        name="Numbers",
        slug="numbers",
        welcome_urls=(
            "https://support.apple.com/guide/numbers/welcome/mac",
            "https://support.apple.com/guide/numbers-ipad/welcome/ipados",
            "https://support.apple.com/guide/numbers-iphone/welcome/ios",
        ),
        platforms=("mac", "ipad", "iphone"),
    ),
    AppSource(
        name="Freeform",
        slug="freeform",
        welcome_urls=(
            "https://support.apple.com/guide/freeform/welcome/mac",
            "https://support.apple.com/guide/freeform-ipad/welcome/ipados",
            "https://support.apple.com/guide/freeform-iphone/welcome/ios",
        ),
        platforms=("mac", "ipad", "iphone"),
    ),
)

REQUEST_DELAY_SEC = 0.4
USER_AGENT = "creatorstudio-help-agent/0.1 (+research; contact: tuochen)"
ALLOWED_DOMAIN = "support.apple.com"
URL_PREFIX = "https://support.apple.com/guide/"
