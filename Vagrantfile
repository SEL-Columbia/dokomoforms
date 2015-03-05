# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Provisioning
  config.vm.provision :shell, :path => "./provision.sh"

  # Every Vagrant virtual environment requires a box to build off of.
  # config.vm.box = "debian-squeeze607-x64-vbox43"
  config.vm.box = "xezpeleta/wheezy64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  # config.vm.box_url = "http://puppet-vagrant-boxes.puppetlabs.com/debian-73-x64-virtualbox-nocm.box"


  config.vm.network :private_network, ip: "192.168.0.200"
  config.vm.hostname = "local.dokomoforms.org"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network :forwarded_port, guest: 80, host: 8080

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "./sql", "/var/sqldump"

  config.vm.synced_folder ".", "/vagrant", id: "vagrant-root", 
    :owner => "vagrant", 
    :group => "www-data",
    :mount_options => ["dmode=777","fmode=666"]

  # config.vm.synced_folder "./app/storage", "/vagrant/app/storage", id: "vagrant-storage",
  #     :owner => "vagrant",
  #     :group => "www-data",
  #     :mount_options => ["dmode=775","fmode=664"]

  # config.vm.synced_folder "./public", "/vagrant/public", id: "vagrant-public",
  #     :owner => "vagrant",
  #     :group => "www-data",
  #     :mount_options => ["dmode=775","fmode=664"]

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider :virtualbox do |vb|
    # Don't boot with headless mode
    # vb.gui = true
  
    # Use VBoxManage to customize the VM. For example to change memory:
    vb.customize ["modifyvm", :id, "--memory", "256"]
  end
 
end