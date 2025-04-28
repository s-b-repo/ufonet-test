#!/usr/bin/env python3 
# -*- coding: utf-8 -*-"
"""
This file is part of the UFONet project, https://ufonet.03c8.net

Copyright (c) 2013/2020 | psy <epsylon@riseup.net>

You should have received a copy of the GNU General Public License along
with UFONet; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os
import gzip
import shutil
import traceback
import subprocess
import socket
from threading import Thread
import time
import re
import traceback
import sys

class AI(Thread):
    def __init__(self, parent):
        super().__init__()
        self.power_on = False
        self.parent = parent
        self.tmp_dir = parent.tmp_dir
        self.target_dir = parent.target_dir

    def find_meat(self):
        self.meats = []
        try:
            for f in os.listdir(os.path.join(self.tmp_dir, "blackhole")):
                if f.endswith('.gz'):
                    print(f"[Info] [AI] Found meat in {f}")
                    self.meats.append(f)
        except Exception:
            print(f"[Info] [AI] No meat in the fridge {self.tmp_dir}blackhole")
            traceback.print_exc()
        return bool(self.meats)

    def process(self):
        categories = {
            'community_zombies.txt.gz': ('meat.txt', []),
            'community_aliens.txt.gz': ('larva.txt', []),
            'community_droids.txt.gz': ('chip.txt', []),
            'community_ucavs.txt.gz': ('arduino.txt', []),
            'community_rpcs.txt.gz': ('mirror.txt', []),
            'community_ntps.txt.gz': ('clock.txt', []),
            'community_dnss.txt.gz': ('label.txt', []),
            'community_snmps.txt.gz': ('glass.txt', [])
        }

        for meat in self.meats:
            path = os.path.join(self.tmp_dir, "blackhole", meat)
            with gzip.open(path, 'rb') as f_in:
                content = f_in.readlines()

                for key, (output_name, incoming_list) in categories.items():
                    if key in meat:
                        output_path = os.path.join(self.tmp_dir, output_name)
                        with open(output_path, 'wb') as f_out:
                            for line in content:
                                incoming_list.append(line)
                                f_out.write(line.strip() + os.linesep)
                        break
            os.remove(path)

        # Test zombies
        try:
            with open(os.path.join(self.tmp_dir, 'meat.tmp'), 'wb') as f_tmp:
                subprocess.call(
                    f'../../ufonet --force-yes -t "{self.tmp_dir}meat.txt"',
                    shell=True,
                    stdout=f_tmp
                )
        except Exception:
            pass

        with open(os.path.join(self.tmp_dir, 'meat.tmp'), 'r') as f_tmp:
            test_output = f_tmp.read()

        if "Not any zombie active" in test_output:
            if not any(incoming for _, incoming in categories.values()):
                print("[Info] [AI] No valid zombies!")
                return

        # Process results
        self.update_army('abductions.txt.gz', 'meat.txt', "Zombies")
        self.update_army('troops.txt.gz', 'larva.txt', "Aliens")
        self.update_army('robots.txt.gz', 'chip.txt', "Droids")
        self.update_army('drones.txt.gz', 'arduino.txt', "UCAVs")
        self.update_army('reflectors.txt.gz', 'mirror.txt', "X-RPCs")
        self.update_army('warps.txt.gz', 'clock.txt', "NTPs")
        self.update_army('crystals.txt.gz', 'label.txt', "DNSs")
        self.update_army('bosons.txt.gz', 'glass.txt', "SNMPs")

    def update_army(self, army_file, community_file, name):
        target_file = os.path.join(self.target_dir, army_file)
        tmp_community_file = os.path.join(self.tmp_dir, community_file)

        try:
            with gzip.open(target_file, 'rb') as f:
                army = f.readlines()
        except FileNotFoundError:
            army = []

        try:
            with open(tmp_community_file, 'r') as f:
                community = f.readlines()
        except FileNotFoundError:
            community = []

        initial = len(army)
        for entity in community:
            if entity.strip() not in army:
                army.append(entity)

        temp_file = os.path.join(self.tmp_dir, f"new_{army_file}")
        with gzip.open(temp_file, 'wb') as f:
            for entity in army:
                f.write(entity.strip() + os.linesep)

        shutil.move(temp_file, target_file)
        print(f"[Info] [AI] {name} tested: {len(community)} / initial: {initial} / final: {len(army)}")

    def run(self):
        self.power_on = True
        print("[Info] [AI] Power On")
        while self.power_on:
            if self.find_meat():
                self.process()
            time.sleep(5)
        print("[Info] [AI] Power Off")

class BlackRay(Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.active = False
        self.sock = None
        self.shining = False

    def run(self):
        self.sock = self.parent.try_bind(9991)
        if self.sock:
            self.sock.listen(1)
            print('[Info] [AI] [BlackRay] Emitting on port 9991')
            self.shining = True
        else:
            print('[Error] [AI] [BlackRay] Failed to emit on port 9991')
            return

        while self.shining:
            try:
                conn, addr = self.sock.accept()
                print(f'[Info] [AI] [BlackRay] Got connection from {addr}')
                data = conn.recv(1024)
                if data and data[:4] == b"SEND":
                    print(f"[Info] [AI] [BlackRay] Meat ready: {data[5:].decode(errors='ignore')}")
                conn.close()
            except socket.timeout:
                continue
            except socket.error as e:
                if not self.shining:
                    print(f"[Error] [AI] [BlackRay] Socket Error /return: {e}")
                    return
                else:
                    print(f"[Error] [AI] [BlackRay] Socket Error /break: {e}")
                    break

        print('[Info] [AI] [BlackRay] End of emission')
        if self.sock:
            self.sock.close()

class Eater(Thread):
    def __init__(self, client, parent):
        super().__init__()
        self.client = client
        self.parent = parent
        self.meat_types = {
            "community_zombies.txt.gz": "meat",
            "community_aliens.txt.gz": "larva",
            "community_droids.txt.gz": "chip",
            "community_ucavs.txt.gz": "arduino",
            "community_rpcs.txt.gz": "mirror",
            "community_ntps.txt.gz": "clock",
            "community_dnss.txt.gz": "label",
            "community_snmps.txt.gz": "glass"
        }

    def run(self):
        print('[Info] [AI] Yum... got meat')
        try:
            data = self.client.recv(4096)
        except Exception:
            data = b""

        if not data:
            self.client.close()
            return

        for meat_file, filename in self.meat_types.items():
            if meat_file.encode() in data:
                try:
                    # Use regex to extract filename from payload
                    match = re.search(rb".*(" + meat_file.encode() + rb").*", data)
                    if match:
                        m = match.group(1).decode(errors='ignore')
                        path = os.path.join(self.parent.tmp_dir, "blackhole", m)
                        with open(path, "wb") as f:
                            f.write(data)
                        print(f'\n[Info] [AI] Got "{path}" Closing media transfer')
                except Exception:
                    pass
                break

        self.client.close()
        self.parent.eater_full(self)


class Absorber(Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.overflow = True
        self._eaters = []
        self.tmp_dir = parent.tmp_dir
        self.sock = None

    def run(self):
        self.sock = self.parent.try_bind(9990)
        if self.sock:
            self.sock.listen(1)
            print('[Info] [AI] Ready to feed on port 9990')
            self.overflow = False
        else:
            print('[Error] [AI] Failed to listen on port 9990')
            return

        while not self.overflow:
            try:
                conn, addr = self.sock.accept()
                print(f'[Info] [AI] Got connection from {addr}')
                eater_thread = Eater(conn, self)
                eater_thread.start()
                self._eaters.append(eater_thread)
            except socket.timeout:
                continue
            except socket.error as e:
                if self.overflow:
                    print(f"[Error] [AI] Socket Error /return: {e}")
                    return
                else:
                    print(f"[Error] [AI] Socket Error /break: {e}")
                    break

        if self.sock:
            self.sock.close()
        print('[Info] [AI] Dinner time is over')

    def eater_full(self, _thread):
        try:
            self._eaters.remove(_thread)
        except ValueError:
            pass

class BlackHole(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.awake = True
        self.tmp_dir = "/tmp/"
        self.target_dir = "/var/www/ufonet/"
        self.blackray = None
        self.absorber = None
        self.computer = None

    def dream(self):
        containers = {
            'abductions.txt.gz': 'abductions',
            'troops.txt.gz': 'troops',
            'robots.txt.gz': 'robots',
            'drones.txt.gz': 'drones',
            'reflectors.txt.gz': 'reflectors',
            'warps.txt.gz': 'warps',
            'crystals.txt.gz': 'crystals',
            'bosons.txt.gz': 'bosons'
        }

        failed = 0

        for filename, label in containers.items():
            path = os.path.join(self.target_dir, filename)
            if not os.path.exists(path):
                try:
                    with gzip.open(path, 'wb') as f:
                        pass
                except Exception:
                    print(f"[Error] [AI] No '{filename}' file in {self.target_dir}")
                    failed += 1

            if not os.access(path, os.W_OK):
                print(f"[Error] [AI] Write access denied for '{label}' file in {self.target_dir}")
                failed += 1

        if failed == len(containers) * 2:
            print("\n[Error] [AI] Cannot find any container... -> [Aborting!]")
            print("\n[Info] [AI] Suspend [Blackhole] with: Ctrl+z")
            sys.exit(2)

        if self.consume():
            os.makedirs(os.path.join(self.tmp_dir, "blackhole"), exist_ok=True)
        else:
            print(f"[Error] [AI] [Blackhole] Unable to consume in {self.tmp_dir}blackhole...")
            sys.exit(2)

        if not os.path.isdir(os.path.join(self.tmp_dir, "blackhole")):
            print(f"[Error] [AI] [Blackhole] Unable to create {self.tmp_dir}blackhole...")
            sys.exit(2)

        self.blackray = BlackRay(self)
        self.absorber = Absorber(self)
        self.computer = AI(self)
        self.awake = False
        print("[Info] [AI] [Blackhole] Having sweet dreams...")

    def consume(self):
        path = os.path.join(self.tmp_dir, "blackhole")
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except OSError as e:
                print(f"[Error] [AI] [Blackhole] Unable to consume: {e}")
                return False
        return True

    def try_bind(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.bind(('', port))
            return s
        except socket.error as e:
            if e.errno == 98:
                time.sleep(3)
                return self.try_bind(port)
            print(f"[Error] [AI] [Blackhole] Socket busy, connection failed on port {port}")
            return None

    def run(self):
        self.dream()
        try:
            self.blackray.start()
            self.absorber.start()
            self.computer.start()

            if not self.blackray.shining or self.absorber.overflow or not self.computer.power_on:
                print("[Info] [AI] Advancing time in another space (waiting for server)\n")
                time.sleep(1)

            while not self.blackray.shining or self.absorber.overflow or not self.computer.power_on:
                time.sleep(1)

            print("\n[Info] [AI] [BlackHole] All up and running...")

            while self.blackray.shining and not self.absorber.overflow and self.computer.power_on:
                time.sleep(1)

        except Exception:
            traceback.print_exc()

        self.awaken()
        print("[Info] [AI] [Blackhole] Lifespan is up...")

    def collapse(self):
        if self.blackray:
            self.blackray.shining = False
        if self.absorber:
            self.absorber.overflow = True
        if self.computer:
            self.computer.power_on = False

        if self.computer:
            self.computer.join()
        if self.blackray:
            self.blackray.join()
        if self.absorber:
            self.absorber.join()

    def awaken(self):
        self.consume()
        self.collapse()
        self.awake = True

if __name__ == "__main__":
    try:
        print("\n[Info] [AI] Initiating void generation sequence...\n")
        print('=' * 22 + '\n')
        app = BlackHole()
        app.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Info] [AI] Terminating void generation sequence...\n")
        if app:
            app.collapse()
    except Exception:
        traceback.print_exc()
        print("\n[Error] [AI] Something wrong creating [Blackhole] -> [Passing!]\n")
