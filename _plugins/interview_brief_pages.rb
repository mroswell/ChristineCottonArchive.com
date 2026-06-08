# Generate a standalone "In Brief" detail page per interview, in each language,
# at /<lang>/interviews/<video-id>/. Data-driven from _data/interviews.json +
# _data/briefs.json; the page body is rendered by _includes/interview-brief-page.html.
# Mirrors the approach of archive_pages.rb (synthesize in-memory Pages).

module Jekyll
  class InterviewBriefPage < Jekyll::PageWithoutAFile
    def initialize(site, lang, video)
      vid   = video['id']
      other = lang == 'en' ? 'fr' : 'en'
      super(site, site.source, File.join(lang, 'interviews', vid), 'index.html')

      self.content = '{% include interview-brief-page.html %}'
      self.data = {
        'layout'           => 'default',
        'lang'             => lang,
        'title'            => video['title'],
        'video_id'         => vid,
        'translation_path' => "/#{other}/interviews/#{vid}/",
      }
    end
  end

  class InterviewBriefGenerator < Generator
    safe true
    priority :normal

    def generate(site)
      videos = site.data['interviews'] || []
      briefs = site.data['briefs'] || {}
      videos.each do |video|
        brief = briefs[video['id']]
        next unless brief && brief['status'] != 'stub'
        %w[en fr].each do |lang|
          site.pages << InterviewBriefPage.new(site, lang, video)
        end
      end
    end
  end
end
