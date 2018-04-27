import requests
import json

class LicencePlate:
    def __init__(self):
        pass

    def _process_json(self,jObject):
        # print('Type:',type(jObject))
        l = json.dumps(jObject)
        l = l.replace("'",'"')
        l = l.replace("False",'false')
        l = l.replace("True",'true')

        obj = json.loads(l)

        output = {}
        for r in obj['results']:
            p = str(r['plate'])
            output['Plate:'] = p
            v = r['vehicle']
            make = v['make']
            makes = []
            for m in make:
                if m['confidence'] > 50:
                    # print('Make:',m['name'],m['confidence'])
                    mdict = {'make':m['name'],'confidence':m['confidence']}
                    makes.append(mdict)
            output["make"] = makes

            model = v['make_model']
            models = []
            for m in model:
                if m['confidence'] > 50:
                    # print('Model:',m['name'],m['confidence'])
                    mdict = {'model':m['name'],'confidence':m['confidence']}
                    models.append(mdict)
            output['model'] = models

            color = v['color']
            colors = []
            for c in color:
                if c['confidence'] > 40:
                    # print('Color:',c['name'],c['confidence'])        
                    cdict = {'color':c['name'],'confidence':c['confidence']}
                    colors.append(cdict)
            output['color'] = colors
        return output
            

    def process(self,filename):
        # form HTTP request
        v = '1'
        c = 'th'
        sk = "sk_e780cf0bb467344b4ac156c8"

        url = "https://api.openalpr.com/v2/recognize?recognize_vehicle=%s&country=%s&secret_key=%s"%(v,c,sk)
        # call ALPR API
        # obtain JSON result
        r = requests.post(url, files={'image': open(filename,'rb')})
        # process JSON result
        result = self._process_json(r.json())
        return result
        # return r.json()

if __name__ == '__main__':
    lp = LicencePlate()
    filename = 'w644.jpg'
    result = lp.process(filename)
    print(result)