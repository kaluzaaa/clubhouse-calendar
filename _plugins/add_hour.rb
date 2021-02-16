module Jekyll
    module AddHourFilter
      def add_hour(date)
        time(date) + 3600
      end
    end
  end
  
  Liquid::Template.register_filter(Jekyll::AddHourFilter)