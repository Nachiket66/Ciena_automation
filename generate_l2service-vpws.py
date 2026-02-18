
from netmiko import ConnectHandler

# Define connection parameters for Ciena 8110 devices
device1 = {
    'device_type': 'generic',       # Use 'generic' for Ciena devices
    'host': '10.180.33.167',          # IP address of device 1
    'username': 'diag',            # SSH username
    'password': 'ciena123',         # SSH password
    'port': 22,                     # Default SSH port
    'global_delay_factor': 2,       # Adjust delay factor if commands take longer
}

device2 = {
    'device_type': 'generic',       # Use 'generic' for Ciena devices
    'host': '10.180.33.169',          # IP address of device 2
    'username': 'diag',
    'password': 'ciena123',
    'port': 22,
    'global_delay_factor': 2,
}



#! /usr/bin/env python3
#
# Retrieve a portion selected by an XPATH expression from the running
# config from the NETCONF server passed on the command line using
# get-config and write the XML configs to files.
#
# $ ./nc03.py broccoli "aaa/authentication/users/user[name='schoenw']"

import sys, os, warnings
warnings.simplefilter("ignore", DeprecationWarning)
# Functions to create services
def gen_classifier(vlan):
    #classifiers classifier 'VLAN3001' filter-entry 'classifier:vtag-stack' vtags '1' vlan-id 3001
    print(f"classifiers classifier \'VLAN{vlan}\' filter-entry \'classifier:vtag-stack\' vtags \'1\' vlan-id {vlan}")

def gen_fds(vlan, port):
    #fds fd 'fd10-3001' mode vpws
    print(f"fds fd \'fd{port}-{vlan}\' mode vpws")

def gen_fps(vlan, port):
    #fps fp 'fp10-3001' fd-name "fd10-3001" logical-port "10" mtu-size 9202 frame-to-cos-map "default-f2c" cos-to-frame-map "default-c2f" classifier-list-precedence 100 stats-collection on classifier-list "VLAN3001"
    print(f"fps fp \'fp{port}-{vlan}\' fd-name \"fd{port}-{vlan}\" logical-port \"{port}\" mtu-size 9202 frame-to-cos-map \"default-f2c\" cos-to-frame-map \"default-c2f\" classifier-list-precedence 100 stats-collection on classifier-list \"VLAN{vlan}\"")
    
def gen_pw(vlan, remote_lbk, port):
    #pseudowires pseudowire 'pw10-3001' mtu 9206 cw-negotiation preferred cc-types "cctype-1" mode spoke pw-loadbalance fat-pw stats-collection on
    #pseudowires pseudowire 'pw10-3001' configured-pw peer-ip "172.24.248.1" pw-id 3001
    print(f"pseudowires pseudowire \'pw{port}-{vlan}\' mtu 9206 cw-negotiation preferred cc-types \"cctype-1\" mode spoke pw-loadbalance fat-pw stats-collection on")
    print(f"pseudowires pseudowire \'pw{port}-{vlan}\' configured-pw peer-ip \"{remote_lbk}\" pw-id {vlan}")

def gen_l2vpn(vlan, remote_lbk, port):
    #l2vpn-services l2vpn 'Ciena-Ciena-VPWS' forwarding-domain "fd10-3001" pseudowire "pw10-3001"
    print(f"l2vpn-services l2vpn \'{vlan}-{remote_lbk}-{vlan}-VPWS\' forwarding-domain \"fd{port}-{vlan}\" pseudowire \"pw{port}-{vlan}\"")

# Functions to remove services
def rm_classifier(vlan):
    #classifiers classifier 'VLAN3001' filter-entry 'classifier:vtag-stack' vtags '1' vlan-id 3001
    print(f"no classifiers classifier \'VLAN{vlan}\'")

def rm_fds(vlan, port):
    #fds fd 'fd10-3001' mode vpws
    print(f"no fds fd \'fd{port}-{vlan}\'")

def rm_fps(vlan, port):
    #fps fp 'fp10-3001' fd-name "fd10-3001" logical-port "10" mtu-size 9202 frame-to-cos-map "default-f2c" cos-to-frame-map "default-c2f" classifier-list-precedence 100 stats-collection on classifier-list "VLAN3001"
    print(f"no fps fp \'fp{port}-{vlan}\'")

def rm_pw(vlan, port):
    #pseudowires pseudowire 'pw10-3001' mtu 9206 cw-negotiation preferred cc-types "cctype-1" mode spoke pw-loadbalance fat-pw stats-collection on
    #pseudowires pseudowire 'pw10-3001' configured-pw peer-ip "172.24.248.1" pw-id 3001
    print(f"no pseudowires pseudowire \'pw{port}-{vlan}\'")

def rm_l2vpn(vlan, remote_lbk):
    #l2vpn-services l2vpn 'Ciena-Ciena-VPWS' forwarding-domain "fd10-3001" pseudowire "pw10-3001"
    print(f"no l2vpn-services l2vpn \'{vlan}-{remote_lbk}-{vlan}-VPWS\'")


if __name__ == '__main__':
    arg_len = len(sys.argv)
#    print(arg_len)
    if arg_len != 7:
        print(f"Usage: {sys.argv[0]} <local port> <start VLAN> <end VLAN> <local lbk> <remote lbk> <create / remove>")
        exit(1)
    start_vlan = int(sys.argv[2])
    end_vlan = int(sys.argv[3])
    num_vlans = (end_vlan - start_vlan) +1
    local_port = int(sys.argv[1])
    mode = (sys.argv[6])
    print (f"{mode}")
    if num_vlans < 0:
        print("end VLAN is less than start VLAN")
    #print(f"Number of VLANS is {num_vlans}")
    current_vlan = start_vlan
    remote_lbk = sys.argv[5]
    if mode == "create":
        while current_vlan < (end_vlan+1):
            gen_classifier(current_vlan)
            gen_fds(current_vlan, local_port)
            gen_fps(current_vlan, local_port)
            gen_pw(current_vlan, remote_lbk, local_port)
            gen_l2vpn(current_vlan, remote_lbk, local_port)
            current_vlan = current_vlan + 1
            print("\n")
        exit(1)
    if mode == "remove":
        while current_vlan < (end_vlan+1):
            rm_l2vpn(current_vlan, remote_lbk)
            rm_pw(current_vlan, local_port)
            rm_fps(current_vlan, local_port)
            rm_fds(current_vlan, local_port)
            rm_classifier(current_vlan)
            current_vlan = current_vlan + 1
            print("\n")
        exit(1)
    print("Invalid Mode")
    exit(1)


#    while current_vlan < (end_vlan+1):
#        gen_classifier(current_vlan)
#        gen_fds(current_vlan, local_port)
#        gen_fps(current_vlan, local_port)
#        gen_pw(current_vlan, remote_lbk, local_port)
#        gen_l2vpn(current_vlan, remote_lbk, local_port)
#
#        current_vlan = current_vlan + 1
#        print("\n")
