import sys

#we using bmv2's tools to read registers,ensure you had P4 env construction is completed. 
sys.path.append(r'~/P4/behavioral-model/tools')
from runtime_CLI import *
import json

names=[u'sketch0',u'sketch1',u'sketch2',
       u'sketch_vote0',u'sketch_vote1',u'sketch_vote2',
       u'sketch_1key0',u'sketch_1key1',u'sketch_1key2',
       u'sketch_2key0',u'sketch_2key1',u'sketch_2key2',]

dict_reg={}

def main():
    register_name=u'MyIngress.sketch0'
    args = get_parser().parse_args()

    standard_client, mc_client = thrift_connect(
        args.thrift_ip, args.thrift_port,
        RuntimeAPI.get_thrift_services(args.pre)
    )

    load_json_config(standard_client, args.json)

    for name in names:
        dict_reg[name] = standard_client.bm_register_read_all(0, u'MyIngress.'+name)

    open("./temp_data",'w').write(json.dumps(dict_reg))
    # print dict_reg

if __name__ == '__main__':
    main()
