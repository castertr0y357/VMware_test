from pyVmomi import vim, vmodl
from pyVim import connect
import atexit


def connect_and_collect_info():

    service_instance = connect.SmartConnectNoSSL(host='',
                                                 user='',
                                                 pwd='',
                                                 port=443)

    atexit.register(connect.Disconnect, service_instance)

    content = service_instance.RetrieveContent()

    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)

    children = containerView.view

    for child in children:
        new_vm = VM(child)
        new_vm.get_vm_info()

        break


class VM:

    def __init__(self, vm):

        self.vm = vm

        # computed fields:
        self.vm_dataStores = ""
        self.vm_perDataStoreUsages = 0

        # pulled fields
        self.vm_name = ""
        self.vm_template = ""
        self.vm_numCPU = ""
        self.vm_cpuReservation = ""
        self.vm_memoryReservation = 0
        self.vm_memorySizeGB = 0
        self.vm_host = ""
        self.vm_host_name = ""
        self.vm_toolsStatus = ""
        self.vm_toolsVersion = ""
        self.vm_guestId = ""
        self.vm_guestFullName = ""
        self.vm_guestAlternateName = ""
        self.vm_description = ""
        self.vm_instanceUuid = ""
        self.vm_dataStore_raw = []
        self.vm_powerState = ""
        self.vm_perDataStoreUsage_Raw = []

    def get_vm_info(self):

        vm = self.vm

        self.vm_name = vm.summary.config.name
        self.vm_template = vm.summary.config.template
        self.vm_numCPU = vm.summary.config.numCpu
        self.vm_cpuReservation = vm.summary.config.cpuReservation
        self.vm_memoryReservation = int(vm.summary.config.memoryReservation / 1024)
        self.vm_memorySizeGB = int(vm.summary.config.memorySizeMB / 1024)
        self.vm_host = vm.runtime.host
        self.vm_host_name = self.vm_host.summary.config.name
        self.vm_toolsStatus = vm.guest.toolsVersionStatus2
        self.vm_toolsVersion = vm.config.tools.toolsVersion
        self.vm_guestId = vm.config.guestId
        self.vm_guestFullName = vm.config.guestFullName
        self.vm_guestAlternateName = vm.config.alternateGuestName
        self.vm_description = vm.config.annotation
        self.vm_instanceUuid = vm.config.instanceUuid
        self.vm_dataStore_raw = vm.datastore
        self.vm_powerState = vm.runtime.powerState
        self.vm_perDataStoreUsage_Raw = vm.storage.perDatastoreUsage

        for ds in self.vm_dataStore_raw:
            self.vm_dataStores += (ds.info.name + ", ")

        for usage in self.vm_perDataStoreUsage_Raw:
            self.vm_perDataStoreUsages += usage.committed

        # Print test

        print("VM Details: ")
        print("")

        print("Name                         : ", self.vm_name)
        print("Power State                  : ", self.vm_powerState)
        print("Is VM a template?            : ", self.vm_template)
        print("Host                         : ", self.vm_host_name)
        print("Number of CPUs               : ", self.vm_numCPU)
        print("CPU reservations             : ", self.vm_cpuReservation)
        print("Memory Allocated in GB       : ", self.vm_memorySizeGB)
        print("Memory reserved in GB        : ", self.vm_memoryReservation)
        print("Are VMware tools installed?  : ", self.vm_toolsStatus)
        print("VMware tools version         : ", self.vm_toolsVersion)
        print("OS short name                : ", self.vm_guestId)
        print("OS full name                 : ", self.vm_guestFullName)
        print("OS alternate name            : ", self.vm_guestAlternateName)
        print("VM description               : ", self.vm_description)
        print("VM UUID                      : ", self.vm_instanceUuid)
        print("Datastore names              : ", self.vm_dataStores)
        print("Datastore usage              : ", self.vm_perDataStoreUsages)

        print("")

        # Check if Physical host has been added

        # if vm_host_name is not in database:
        new_host = Host(self.vm_host)
        new_host.get_host_info()

        # Check if datastore has been added

        for ds in self.vm_dataStore_raw:
            # if ds.info.name is not in the database
            new_datastore = Datastore(ds)
            new_datastore.get_datastore_info()

        # Relevant VM attributes


class Host:

    def __init__(self, vm_host):

        self.host = vm_host
        self.host_name = ""
        self.host_powerstate = ""
        self.host_uptime = ""
        self.host_mgmt_ip = ""
        self.host_vendor = ""
        self.host_model = ""
        self.host_cpu_model = ""
        self.host_cpu_cores = 0
        self.host_cpu_speed_in_Ghz = 0
        self.host_cpu_total_capacity = 0
        self.host_cpu_consumed_in_Ghz = 0
        self.host_memory_size_in_GB = 0
        self.host_memory_consumed_in_GB = 0
        self.host_num_nics = ""
        self.host_num_hbas = ""
        self.host_uuid = ""
        self.host_other_info = ""
        self.host_nic_info = ""

    def get_host_info(self):
        host = self.host

        self.host_name = host.summary.config.name
        self.host_powerstate = host.runtime.powerState
        self.host_uptime = host.summary.quickStats.uptime
        self.host_mgmt_ip = host.summary.managementServerIp
        self.host_vendor = host.summary.hardware.vendor
        self.host_model = host.summary.hardware.model
        self.host_cpu_model = host.summary.hardware.cpuModel
        self.host_cpu_cores = host.summary.hardware.numCpuCores
        self.host_cpu_speed_in_Ghz = (host.summary.hardware.cpuMhz / 1024)
        self.host_cpu_total_capacity = self.host_cpu_cores * self.host_cpu_speed_in_Ghz
        self.host_cpu_consumed_in_Ghz = (host.summary.quickStats.overallCpuUsage / 1024)
        self.host_memory_size_in_GB = (host.summary.hardware.memorySize / (1024 * 1024 * 1024))
        self.host_memory_consumed_in_GB = (host.summary.quickStats.overallMemoryUsage / 1024)
        self.host_num_nics = host.summary.hardware.numNics
        self.host_num_hbas = host.summary.hardware.numHBAs
        self.host_uuid = host.summary.hardware.uuid
        self.host_other_info = host.summary.hardware.otherIdentifyingInfo
        self.host_nic_info = host.config.network.pnic

        # Print test

        print("Host Details:")
        print("")

        print("Name                         : ", self.host_name)
        print("Power State                  : ", self.host_powerstate)
        print("Uptime                       : ", self.host_uptime)
        print("Management IP                : ", self.host_mgmt_ip)
        print("Host Vendor                  : ", self.host_vendor)
        print("Host Model                   : ", self.host_model)
        print("CPU Model                    : ", self.host_cpu_model)
        print("Number of CPU cores          : ", self.host_cpu_cores)
        print("CPU speed in Ghz             : ", self.host_cpu_speed_in_Ghz)
        print("Total CPU resources in Ghz   : ", self.host_cpu_total_capacity)
        print("Used CPU resources in Ghz    : ", self.host_cpu_consumed_in_Ghz)
        print("Total memory in GB           : ", self.host_memory_size_in_GB)
        print("Used memory in GB            : ", self.host_memory_consumed_in_GB)
        print("Number of NICs               : ", self.host_num_nics)
        print("Number of HBAs               : ", self.host_num_hbas)
        print("Host UUID                    : ", self.host_uuid)
        # print("Other info                   : ", host_other_info)

        print("")
        """
        print("     Nic details: ")

        for nic in self.host_nic_info:
            print("     NIC device                   : ", nic.device)
            print("     NIC driver                   : ", nic.driver)
            # print("     NIC speed                    : ", nic.linkSpeed.speedMb)
            print("")
            """


class Datastore:

    def __init__(self, datastore):

        self.ds = datastore
        self.ds_name = ""
        self.ds_type = ""
        self.ds_capacity_in_TB = 0
        self.ds_freeSpace_in_TB = 0
        self.ds_url = ""

    def get_datastore_info(self):
        ds = self.ds

        self.ds_name = ds.summary.name
        self.ds_type = ds.summary.type
        self.ds_capacity_in_TB = (ds.summary.capacity / (1024 * 1024 * 1024 * 1024))
        self.ds_freeSpace_in_TB = (ds.summary.freeSpace / (1024 * 1024 * 1024 * 1024))
        self.ds_url = ds.summary.url

        # Print test
        print("Datastore Details: ")
        print("")

        print("Name                         : ", self.ds_name)
        print("Type                         : ", self.ds_type)
        print("Size in TB                   : ", self.ds_capacity_in_TB)
        print("Available space in TB        : ", self.ds_freeSpace_in_TB)
        print("Datastore URL                : ", self.ds_url)

        print("")


connect_and_collect_info()
