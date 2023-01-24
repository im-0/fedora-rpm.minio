# TODO: Enable debuginfo (disabled for f35).
%global debug_package %{nil}

%global orig_version_date 2023-01-20
%global orig_version_time 02-05-44
%global orig_version %{orig_version_date}T%{lua: print(rpm.expand("%{orig_version_time}"):gsub("-", ":") .. "Z")}
%global orig_tag RELEASE.%{orig_version_date}T%{orig_version_time}Z

Name:       minio
Version:    %{lua: print(rpm.expand("%{orig_version_date}"):gsub("-", ".") .. "." .. rpm.expand("%{orig_version_time}"):gsub("-", "."))}
Release:    1%{?dist}
Summary:    High Performance Object Storage

License:    AGPLv3
URL:        https://github.com/minio/minio/
Source0:    https://github.com/minio/minio/archive/%{orig_tag}/%{name}-%{orig_tag}.tar.gz

# $ GOPROXY=https://proxy.golang.org go mod vendor -v
# Contains minio-$TAG/vendor/*.
Source1:    %{name}-%{orig_tag}.go-mod-vendor.tar.xz

Source2:    minio.service
Source3:    minio

Patch0:     0001-Do-not-check-for-cross-device-mounts.patch

ExclusiveArch:  x86_64 aarch64 ppc64le s390x %{arm}

BuildRequires:  systemd-rpm-macros
BuildRequires:  golang >= 1.18


%description
MinIO is a High Performance Object Storage released under GNU Affero
General Public License v3.0. It is API compatible with Amazon S3 cloud
storage service. Use MinIO to build high performance infrastructure for
machine learning, analytics and application data workloads.


%prep
%autosetup -p1 -b1 -n %{name}-%{orig_tag}

sed -i 's,^\([[:space:]]*Version[[:space:]]*=[[:space:]]*\)".*$,\1"%{orig_version}",' cmd/build-constants.go
sed -i 's,^\([[:space:]]*ReleaseTag[[:space:]]*=[[:space:]]*\)".*$,\1"%{orig_tag}",' cmd/build-constants.go


%build
export GO111MODULE="on"
export CGO_ENABLED=0
go build -v \
        -tags kqueue \
        -ldflags "-B 0x$(head -c20 /dev/urandom | od -An -tx1 | tr -d ' \n')"


%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_unitdir}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/minio/certs
mkdir -p %{buildroot}/%{_sharedstatedir}/minio

cp %{SOURCE2} %{buildroot}/%{_unitdir}/
cp %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/
mv minio %{buildroot}/%{_bindir}/


%files
%attr(0750,root,minio) %caps(cap_net_bind_service=ep) %{_bindir}/minio
%{_unitdir}/minio.service
%attr(0640,root,minio) %config(noreplace) %{_sysconfdir}/sysconfig/minio
%attr(0750,root,minio) %dir %{_sysconfdir}/minio
%attr(0750,root,minio) %dir %{_sysconfdir}/minio/certs
%attr(0750,minio,minio) %dir %{_sharedstatedir}/minio


%pre
getent group minio >/dev/null || groupadd -r minio
getent passwd minio >/dev/null || \
        useradd -r -s /sbin/nologin -d %{_sharedstatedir}/minio -M \
        -c 'MinIO High Performance Object Storage' -g minio minio
exit 0


%post
%systemd_post minio.service


%preun
%systemd_preun minio.service


%postun
%systemd_postun_with_restart minio.service


%changelog
* Tue Jan 24 2023 Ivan Mironov <mironov.ivan@gmail.com> - 2023.01.20.02.05.44-1
- Update to RELEASE.2023-01-20T02-05-44Z

* Sun Sep 18 2022 Ivan Mironov <mironov.ivan@gmail.com> - 2022.09.17.00.09.45-1
- Update to RELEASE.2022-09-17T00-09-45Z

* Wed May 11 2022 Ivan Mironov <mironov.ivan@gmail.com> - 2022.05.08.23.50.31-1
- Update to RELEASE.2022-05-08T23-50-31Z

* Tue Sep 21 2021 Ivan Mironov <mironov.ivan@gmail.com> - 2021.09.18.18.09.59-1
- Update to RELEASE.2021-09-18T18-09-59Z

* Sat Jun 12 2021 Ivan Mironov <mironov.ivan@gmail.com> - 2021.06.09.18.51.39-1
- Initial packaging
