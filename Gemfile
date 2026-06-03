source "https://rubygems.org"

# Modern Jekyll (4.x). We don't use the `github-pages` gem because it pins
# Jekyll to 3.9.x, which is incompatible with Ruby 3.4+ (csv was removed
# from default gems). Instead, the site is built and deployed via a GitHub
# Actions workflow that runs the same Jekyll version locally and on CI.
gem "jekyll", "~> 4.3"

group :jekyll_plugins do
  gem "jekyll-sitemap"
  gem "jekyll-seo-tag"
  gem "jekyll-redirect-from"
end

# Default gems removed from Ruby 3.4+ that Jekyll/dependencies still touch.
gem "csv"
gem "base64"
gem "bigdecimal"
gem "logger"

# Built-in webrick (removed from Ruby 3.0 stdlib) — needed for `jekyll serve`.
gem "webrick"
