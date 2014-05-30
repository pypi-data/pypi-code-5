from django.forms.widgets import Widget
from django.conf import settings
from django.template import Template, Context


class ImagePreviewWidget(Widget):

    def render(self, name, value, attrs=None):
    	width = attrs.get("width", "100px")
    	height = attrs.get("height", "auto")
    	template = Template("""
    		<input type="file" name="{{name}}" />
            <div>
    		<img src="{% if value %}{{value.url}}{% endif%}" alt="{{name}}" id="{{name}}_preview" style="width:{{width}}; height: {{height}}; {%if not value %}display:none;{% endif %}"/>
            </div>
            <script type="text/javascript">
            jQuery("input[name='{{name}}']").change(function(event){
                var jQuery = window.jQuery || window.$;
            	var oFReader = new FileReader();
        		oFReader.readAsDataURL(event.target.files[0]);
				
				oFReader.onload = function (oFREvent) {
            		jQuery("#{{name}}_preview").attr("src",oFREvent.target.result).show();
       		    };

            });
            </script>
            """)
    	return template.render(Context({"name": name, "value": value, "width":width, "height": height}))

    def value_from_datadict(self, data, files, name):
        return None if data[name] == "None" else data[name]

