"""
Django management command for security scanning.
Usage: python manage.py security_scan [--sbom] [--cve] [--report]
"""
from django.core.management.base import BaseCommand
from phishing_portal.supply_chain_security import SupplyChainSecurity
import json


class Command(BaseCommand):
    help = 'Run security scans: SBOM generation, CVE scanning, dependency analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sbom',
            action='store_true',
            help='Generate Software Bill of Materials',
        )
        parser.add_argument(
            '--cve',
            action='store_true',
            help='Scan for known CVEs',
        )
        parser.add_argument(
            '--dependencies',
            action='store_true',
            help='Analyze dependencies',
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate full security report',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path',
        )

    def handle(self, *args, **options):
        scanner = SupplyChainSecurity()
        
        if options['sbom']:
            self.stdout.write(self.style.SUCCESS('Generating SBOM...'))
            sbom = scanner.generate_sbom(options.get('output') or 'sbom.json')
            self.stdout.write(json.dumps(sbom, indent=2))
            self.stdout.write(self.style.SUCCESS('\nSBOM generated successfully'))
        
        elif options['cve']:
            self.stdout.write(self.style.SUCCESS('Scanning for CVEs...'))
            cve_results = scanner.scan_for_cves()
            self.stdout.write(json.dumps(cve_results, indent=2))
            if cve_results.get('total_vulnerabilities', 0) > 0:
                self.stdout.write(self.style.WARNING(f"\nFound {cve_results['total_vulnerabilities']} vulnerabilities"))
            else:
                self.stdout.write(self.style.SUCCESS('\nNo known vulnerabilities found'))
        
        elif options['dependencies']:
            self.stdout.write(self.style.SUCCESS('Analyzing dependencies...'))
            deps = scanner.analyze_dependencies()
            self.stdout.write(json.dumps(deps, indent=2))
            if deps.get('outdated_packages'):
                self.stdout.write(self.style.WARNING(f"\nFound {len(deps['outdated_packages'])} outdated packages"))
        
        elif options['report']:
            self.stdout.write(self.style.SUCCESS('Generating security report...'))
            report = scanner.generate_security_report(options.get('output') or 'security_report.json')
            self.stdout.write(json.dumps(report, indent=2))
            self.stdout.write(self.style.SUCCESS('\nSecurity report generated successfully'))
        
        else:
            self.stdout.write(self.style.ERROR('Please specify --sbom, --cve, --dependencies, or --report'))
            self.stdout.write('Example: python manage.py security_scan --report')

