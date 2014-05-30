from pyolite import Pyolite

# initial olite object
admin_repository = '/home/wok/presslabs/gitolite-admin/'
olite = Pyolite(admin_repository=admin_repository)

# get user by name
vlad = olite.users.get(name='vlad')

vlad.keys.remove("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCmBvfyqhQI6Y0oyEhQ6HjE4XGRohOegWZlzArS13R1snzE2/PIOo3DPlXbZ5ktdtXhI3wftsy0yok4bQSwxbaUFAByEpWawH0TLr3RITLgayGllNDjDhciSWTz8rveu0+ojnJl8XhDxmhocyOnTNdCPsXMoZ0dD+Xj1cOn8koFYXSTgx75Ope94F5McJtekiCP84reiblHqCY+AtrHdDY+4L8T8ZesPb9ZaRQKeSNMB0WxBoNqbmSPdFl3fcazT6RATNalhCYIFEJhzzcBgZzjUEiBagvvUEl6rWMyPtsKWSW2eSLs/t+6ku/LblBM6/tZXdQhx6yLIDYHYeFWJGoZ vladtemian@gmail.com")
