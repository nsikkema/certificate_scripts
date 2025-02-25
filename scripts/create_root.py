import argparse
import pathlib
import subprocess
import tempfile

from internal.paths import scratch_path
from mako.template import Template

__all__ = ["main"]

from scripts.internal.paths import templates_folder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_directory",
        "-o",
        help="where to output the ca-cert folder",
        required=True,
    )
    parser.add_argument("--country", help="country code", required=True)
    parser.add_argument("--state", help="state code", required=True)
    parser.add_argument("--locality", help="city name", required=True)
    parser.add_argument("--organization", help="organization name", required=True)
    parser.add_argument(
        "--organization_unit", help="organization unit name", required=True
    )
    parser.add_argument("--common_name", help="common name", required=True)
    parser.add_argument("--email_address", help="email address", required=True)
    parser.add_argument(
        "--expiration", help="expiration in years", type=int, default=20
    )
    arguments = parser.parse_args()

    expiration_days = int(arguments.expiration) * 365

    output_directory = pathlib.Path(arguments.output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    ca_cert_path = output_directory / "ca-cert"

    if ca_cert_path.exists():
        print("The ca-cert folder already exists, do you want to overwrite it?")
        answer = input("Enter yes to continue: ").lower()
        if answer != "yes":
            return

    with tempfile.TemporaryDirectory(dir=scratch_path) as temp_directory:
        temp_directory_path = pathlib.Path(temp_directory)
        temp_ca_cert_path = temp_directory_path / "ca-cert"
        temp_ca_cert_path.mkdir(parents=True, exist_ok=True)
        ca_key_path = temp_ca_cert_path / "ca.key"
        subprocess.call(["openssl", "genrsa", "-out", f"{ca_key_path}", "4096"])
        subprocess.call(["chmod", "400", f"{ca_key_path}"])

        template_path = templates_folder / "template_ca.cnf"

        template = Template(filename=str(template_path))
        configuration_string = template.render(
            template_country_name=arguments.country,
            template_state_or_province_name=arguments.state,
            template_locality_name=arguments.locality,
            template_organization_name=arguments.organization,
            template_organization_unit_name=arguments.organization_unit,
            template_common_name=arguments.common_name,
            template_email_address=arguments.email_address,
        )

        configuration_path = temp_ca_cert_path / "ca.cnf"
        configuration_path.write_text(configuration_string)

        temp_ca_csr_path = temp_ca_cert_path / "ca.csr"
        temp_ca_crt_path = temp_ca_cert_path / "ca.crt"

        subprocess.call(
            [
                "openssl",
                "req",
                "-new",
                "-key",
                f"{ca_key_path}",
                "-out",
                f"{temp_ca_csr_path}",
                "-config",
                f"{configuration_path}",
            ]
        )

        subprocess.call(
            [
                "openssl",
                "x509",
                "-req",
                "-days",
                str(expiration_days),
                "-in",
                f"{temp_ca_csr_path}",
                "-signkey",
                f"{ca_key_path}",
                "-out",
                f"{temp_ca_crt_path}",
            ]
        )

        pass


if __name__ == "__main__":
    main()
