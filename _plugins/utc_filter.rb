module Jekyll
    module UTCFilter
      def to_utc(date)
        time(date).utc
      end
    end
  end
  
  Liquid::Template.register_filter(Jekyll::UTCFilter)