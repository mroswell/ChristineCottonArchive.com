# Synthesize Jekyll pages for the captured Markdown files under archive/
# without modifying them on disk. The .md files in archive/documents,
# archive/pages, and archive/pages_en are preservation artifacts — they
# don't carry YAML front matter, so vanilla Jekyll skips them. This
# generator wraps each into an in-memory Page with the right layout +
# language so they render at /archive/.../slug/.

module Jekyll
  class ArchivePage < Page
    def initialize(site, base, dir, name, defaults)
      @site = site
      @base = base
      @dir  = dir
      @name = name

      slug = name.sub(/\.md\z/, '')

      # Read the file as UTF-8 — captured archive files contain French accents,
      # the book has em-dashes, etc.
      @content = File.read(File.join(base, dir, name), encoding: 'UTF-8')

      # Try to surface a sensible page title from the first Markdown H1.
      title = nil
      @content.each_line do |line|
        if line =~ /\A#\s+(.+?)\s*\z/
          title = Regexp.last_match(1)
          break
        end
      end

      @data = defaults.dup
      @data['title'] ||= title || slug

      # Heuristic: a filename containing _FR or _French is French; _EN or
      # _English is English. Used for archive/documents/ where the default
      # block doesn't pre-assign a language.
      unless @data['lang']
        case name
        when /_FR(?:_|\.|$)/, /_French/i then @data['lang'] = 'fr'
        when /_EN(?:_|\.|$)/, /_English/i then @data['lang'] = 'en'
        end
      end

      # Jekyll's Page#process needs @name set so it can compute the URL.
      # We set the basename and ext explicitly because we're bypassing
      # the constructor that would normally do this.
      @ext     = '.md'
      @basename = slug
      process(name)
    end
  end

  class ArchiveGenerator < Generator
    safe true
    priority :high

    CONFIG = {
      'archive/documents' => { 'layout' => 'document' },
      'archive/pages'     => { 'layout' => 'default', 'lang' => 'fr' },
      'archive/pages_en'  => { 'layout' => 'default', 'lang' => 'en' },
    }.freeze

    def generate(site)
      CONFIG.each do |dir, defaults|
        abs = File.join(site.source, dir)
        next unless File.directory?(abs)
        Dir.entries(abs).sort.each do |name|
          next unless name.end_with?('.md')
          next if name.start_with?('.')
          page = ArchivePage.new(site, site.source, dir, name, defaults)
          site.pages << page
        end
      end
    end
  end
end
