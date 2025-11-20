# Central source of truth for blog content

BLOG_POSTS = [
    {
        "slug": "fake-password-reset-emails",
        "title": "How to Spot a Fake Password Reset Email",
        "tag": "Email Security",
        "read_time": "3 min read",
        "published": "2025-01-15",
        "summary": "Check the sender, hover over links, and never enter your password directly from an email.",
        "content": """
        <h2>1. Check the real sender</h2>
        <p>Attackers often imitate legitimate domains using tiny variations. Look for misspellings like <code>amaz0n.com</code> instead of <code>amazon.com</code>, or <code>microsft.com</code> instead of <code>microsoft.com</code>.</p>
        
        <h2>2. Never click password links</h2>
        <p>Legitimate companies will never ask you to reset your password via an email link. Always go directly to the website by typing the URL yourself, or use a bookmarked link.</p>
        
        <h2>3. Hover to verify links</h2>
        <p>Before clicking any link, hover your mouse over it to see the actual destination URL. If it doesn't match the company's official domain, it's likely a phishing attempt.</p>
        
        <h2>4. What to do if you already clicked?</h2>
        <ul>
            <li>Reset your password immediately on the official website</li>
            <li>Report the message to your security team</li>
            <li>Enable multi-factor authentication (MFA) if not already activated</li>
            <li>Check for any suspicious activity on your account</li>
        </ul>
        """
    },
    {
        "slug": "urgent-requests-scare-tactics",
        "title": "Urgent Requests and Scare Tactics",
        "tag": "Social Engineering",
        "read_time": "4 min read",
        "published": "2025-01-14",
        "summary": "Attackers love words like 'urgent', 'final notice', and 'account suspended'. Learn what to do instead of panicking.",
        "content": """
        <h2>Why attackers use urgency</h2>
        <p>Phishing emails often create a sense of urgency to make you act without thinking. Common phrases include:</p>
        <ul>
            <li>"Your account will be closed in 24 hours"</li>
            <li>"Immediate action required"</li>
            <li>"Final notice - act now"</li>
            <li>"Your payment failed - update now"</li>
        </ul>
        
        <h2>Red flags to watch for</h2>
        <p>Legitimate companies rarely use extreme urgency. If you see:</p>
        <ul>
            <li>Multiple exclamation marks (!!!)</li>
            <li>Threats of account closure</li>
            <li>Demands for immediate payment</li>
            <li>Warnings about legal action</li>
        </ul>
        <p>Take a step back and verify the message through official channels.</p>
        
        <h2>What to do instead</h2>
        <p>When you receive an urgent email:</p>
        <ol>
            <li>Don't click any links in the email</li>
            <li>Contact the company directly using their official website or phone number</li>
            <li>Verify the request through a separate communication channel</li>
            <li>Report suspicious emails to your IT security team</li>
        </ol>
        """
    },
    {
        "slug": "links-attachments-qr-codes",
        "title": "Links, Attachments, and QR Codes",
        "tag": "Safe Clicking",
        "read_time": "5 min read",
        "published": "2025-01-13",
        "summary": "Simple checks before you click can stop most phishing attacks – including QR code scams.",
        "content": """
        <h2>1. Verify links before clicking</h2>
        <p>Always hover over links to see the actual destination. Look for:</p>
        <ul>
            <li>HTTPS (not HTTP) for secure connections</li>
            <li>Correct domain spelling</li>
            <li>No suspicious subdomains</li>
        </ul>
        
        <h2>2. Be cautious with attachments</h2>
        <p>Never open attachments from unknown senders. Even if the sender seems familiar:</p>
        <ul>
            <li>Verify the sender's email address carefully</li>
            <li>Scan attachments with antivirus software</li>
            <li>Be especially wary of .exe, .zip, or .docm files</li>
        </ul>
        
        <h2>3. QR code safety</h2>
        <p>QR codes are becoming a new attack vector. Before scanning:</p>
        <ul>
            <li>Only scan QR codes from trusted sources</li>
            <li>Check the URL before proceeding after scanning</li>
            <li>Be suspicious of QR codes in unexpected locations</li>
            <li>Use a QR scanner that shows the URL before opening</li>
        </ul>
        
        <h2>4. Best practices</h2>
        <p>When in doubt:</p>
        <ul>
            <li>Type URLs manually instead of clicking links</li>
            <li>Use bookmarks for frequently visited sites</li>
            <li>Keep your browser and security software updated</li>
            <li>Report suspicious links to your security team</li>
        </ul>
        """
    },
    {
        "slug": "ceo-fraud-invoice-scam",
        "title": "CEO Fraud and Invoice Scams",
        "tag": "Business Email",
        "read_time": "4 min read",
        "published": "2025-01-12",
        "summary": "Learn how attackers impersonate executives to trick employees into transferring money or revealing sensitive information.",
        "content": """
        <h2>What is CEO fraud?</h2>
        <p>CEO fraud (also called Business Email Compromise or BEC) involves attackers impersonating company executives to trick employees into:</p>
        <ul>
            <li>Transferring money to fraudulent accounts</li>
            <li>Revealing sensitive company information</li>
            <li>Changing payment details for legitimate vendors</li>
        </ul>
        
        <h2>How to spot CEO fraud</h2>
        <p>Warning signs include:</p>
        <ul>
            <li>Emails from executives asking for urgent wire transfers</li>
            <li>Requests to keep the transaction confidential</li>
            <li>Slight variations in email addresses (e.g., john.smith@company.com vs john.smith@companyy.com)</li>
            <li>Unusual requests that bypass normal procedures</li>
        </ul>
        
        <h2>Invoice scams</h2>
        <p>Attackers may send fake invoices that look legitimate. Always:</p>
        <ul>
            <li>Verify invoice details with the vendor directly</li>
            <li>Check payment information matches previous records</li>
            <li>Confirm any changes to payment methods through official channels</li>
        </ul>
        
        <h2>Protection measures</h2>
        <p>To protect your organization:</p>
        <ul>
            <li>Establish clear procedures for financial transactions</li>
            <li>Require verbal confirmation for large transfers</li>
            <li>Train employees to recognize BEC attempts</li>
            <li>Use email authentication (SPF, DKIM, DMARC)</li>
        </ul>
        """
    },
    {
        "slug": "mfa-importance",
        "title": "Why Multi-Factor Authentication Matters",
        "tag": "Account Security",
        "read_time": "3 min read",
        "published": "2025-01-11",
        "summary": "MFA adds an extra layer of security that can prevent 99.9% of account takeovers, even if your password is compromised.",
        "content": """
        <h2>What is MFA?</h2>
        <p>Multi-Factor Authentication (MFA) requires more than just a password to access your account. It typically combines:</p>
        <ul>
            <li>Something you know (password)</li>
            <li>Something you have (phone, authenticator app)</li>
            <li>Something you are (biometric)</li>
        </ul>
        
        <h2>Why MFA is essential</h2>
        <p>Even strong passwords can be compromised through:</p>
        <ul>
            <li>Data breaches</li>
            <li>Phishing attacks</li>
            <li>Keyloggers</li>
            <li>Password reuse across sites</li>
        </ul>
        <p>MFA ensures that even if your password is stolen, attackers still can't access your account.</p>
        
        <h2>Types of MFA</h2>
        <p>Common MFA methods include:</p>
        <ul>
            <li><strong>SMS codes:</strong> Text message with a code</li>
            <li><strong>Authenticator apps:</strong> More secure than SMS (e.g., Google Authenticator, Microsoft Authenticator)</li>
            <li><strong>Hardware tokens:</strong> Physical devices that generate codes</li>
            <li><strong>Biometrics:</strong> Fingerprint or face recognition</li>
        </ul>
        
        <h2>Best practices</h2>
        <ul>
            <li>Enable MFA on all accounts that support it</li>
            <li>Prefer authenticator apps over SMS when possible</li>
            <li>Keep backup codes in a secure location</li>
            <li>Never share your MFA codes with anyone</li>
        </ul>
        """
    },
    {
        "slug": "password-hygiene",
        "title": "Password Hygiene Best Practices",
        "tag": "Account Security",
        "read_time": "4 min read",
        "published": "2025-01-10",
        "summary": "Learn how to create strong, unique passwords and manage them securely without compromising convenience.",
        "content": """
        <h2>Create strong passwords</h2>
        <p>A strong password should:</p>
        <ul>
            <li>Be at least 12 characters long (longer is better)</li>
            <li>Include a mix of uppercase, lowercase, numbers, and symbols</li>
            <li>Avoid dictionary words and personal information</li>
            <li>Use passphrases: multiple random words strung together</li>
        </ul>
        
        <h2>Use unique passwords</h2>
        <p>Never reuse passwords across different accounts. If one account is compromised, all your accounts become vulnerable. Consider using a password manager to:</p>
        <ul>
            <li>Generate strong, unique passwords</li>
            <li>Store passwords securely</li>
            <li>Auto-fill passwords safely</li>
        </ul>
        
        <h2>Password managers</h2>
        <p>Popular password managers include:</p>
        <ul>
            <li>Bitwarden (free and open-source)</li>
            <li>1Password</li>
            <li>LastPass</li>
            <li>Built-in browser password managers</li>
        </ul>
        
        <h2>What to avoid</h2>
        <ul>
            <li>Don't use personal information (birthdays, names, addresses)</li>
            <li>Don't use common patterns (123456, password, qwerty)</li>
            <li>Don't share passwords with colleagues or friends</li>
            <li>Don't write passwords down in plain text</li>
        </ul>
        """
    },
    {
        "slug": "ransomware-basics",
        "title": "Understanding Ransomware Threats",
        "tag": "Malware",
        "read_time": "5 min read",
        "published": "2025-01-09",
        "summary": "Ransomware can lock your files and demand payment. Learn how to protect yourself and what to do if attacked.",
        "content": """
        <h2>What is ransomware?</h2>
        <p>Ransomware is malicious software that encrypts your files and demands payment (usually in cryptocurrency) to restore access. It can spread through:</p>
        <ul>
            <li>Malicious email attachments</li>
            <li>Compromised websites</li>
            <li>Network vulnerabilities</li>
            <li>USB drives</li>
        </ul>
        
        <h2>How ransomware works</h2>
        <p>The attack typically follows these steps:</p>
        <ol>
            <li>Malware is installed on your system</li>
            <li>Files are encrypted and become inaccessible</li>
            <li>A ransom note appears demanding payment</li>
            <li>Attackers threaten to delete files if payment isn't made</li>
        </ol>
        
        <h2>Prevention strategies</h2>
        <ul>
            <li><strong>Regular backups:</strong> Keep offline backups of important files</li>
            <li><strong>Keep software updated:</strong> Install security patches promptly</li>
            <li><strong>Be cautious with emails:</strong> Don't open suspicious attachments</li>
            <li><strong>Use antivirus software:</strong> Keep it updated and running</li>
            <li><strong>Network segmentation:</strong> Limit access between systems</li>
        </ul>
        
        <h2>If you're attacked</h2>
        <p>If ransomware strikes:</p>
        <ul>
            <li>Disconnect from the network immediately</li>
            <li>Don't pay the ransom (it doesn't guarantee file recovery)</li>
            <li>Contact your IT security team immediately</li>
            <li>Report the incident to law enforcement</li>
            <li>Restore from backups if available</li>
        </ul>
        """
    },
    {
        "slug": "shoulder-surfing",
        "title": "Protecting Against Shoulder Surfing",
        "tag": "Physical Security",
        "read_time": "3 min read",
        "published": "2025-01-08",
        "summary": "Learn how to protect sensitive information from prying eyes in public spaces and shared work environments.",
        "content": """
        <h2>What is shoulder surfing?</h2>
        <p>Shoulder surfing is when someone watches over your shoulder to steal passwords, PINs, or other sensitive information. It commonly happens in:</p>
        <ul>
            <li>Public spaces (cafes, airports, trains)</li>
            <li>Open office environments</li>
            <li>Shared workspaces</li>
            <li>ATM machines</li>
        </ul>
        
        <h2>Protection techniques</h2>
        <p>To protect yourself:</p>
        <ul>
            <li><strong>Use privacy screens:</strong> Screen filters that limit viewing angles</li>
            <li><strong>Position your screen:</strong> Angle it away from public view</li>
            <li><strong>Be aware of your surroundings:</strong> Check for people watching</li>
            <li><strong>Use password managers:</strong> Auto-fill reduces typing visible passwords</li>
        </ul>
        
        <h2>When working remotely</h2>
        <p>Extra precautions for remote work:</p>
        <ul>
            <li>Use a private room when possible</li>
            <li>Close blinds or curtains</li>
            <li>Be mindful of video call backgrounds</li>
            <li>Lock your screen when stepping away</li>
        </ul>
        
        <h2>Best practices</h2>
        <ul>
            <li>Never enter passwords in public view</li>
            <li>Use biometric authentication when available</li>
            <li>Enable screen lock after inactivity</li>
            <li>Be cautious with sensitive documents in public</li>
        </ul>
        """
    },
    {
        "slug": "safe-remote-working",
        "title": "Secure Remote Working Practices",
        "tag": "Remote Work",
        "read_time": "4 min read",
        "published": "2025-01-07",
        "summary": "Working from home or public spaces requires extra security awareness. Learn how to protect company data remotely.",
        "content": """
        <h2>Secure your home network</h2>
        <p>Your home Wi-Fi is your first line of defense:</p>
        <ul>
            <li>Use WPA3 encryption (or WPA2 if WPA3 isn't available)</li>
            <li>Change default router passwords</li>
            <li>Enable network firewall</li>
            <li>Keep router firmware updated</li>
        </ul>
        
        <h2>Use VPN when necessary</h2>
        <p>When connecting to company resources:</p>
        <ul>
            <li>Always use the company VPN for sensitive work</li>
            <li>Verify VPN connection before accessing data</li>
            <li>Don't use public Wi-Fi without VPN</li>
            <li>Disconnect VPN when not needed</li>
        </ul>
        
        <h2>Physical security</h2>
        <p>Protect your devices and workspace:</p>
        <ul>
            <li>Lock your screen when away from your desk</li>
            <li>Store devices securely when not in use</li>
            <li>Be mindful of what's visible in video calls</li>
            <li>Shred sensitive documents before disposal</li>
        </ul>
        
        <h2>Public spaces</h2>
        <p>If you must work in public:</p>
        <ul>
            <li>Avoid accessing sensitive information</li>
            <li>Use a privacy screen</li>
            <li>Be aware of your surroundings</li>
            <li>Use mobile hotspot instead of public Wi-Fi when possible</li>
        </ul>
        
        <h2>Device management</h2>
        <ul>
            <li>Keep operating systems and software updated</li>
            <li>Use company-approved devices when possible</li>
            <li>Enable full disk encryption</li>
            <li>Install and update antivirus software</li>
        </ul>
        """
    },
    {
        "slug": "reporting-suspicious-emails",
        "title": "How to Report Suspicious Emails",
        "tag": "Best Practices",
        "read_time": "3 min read",
        "published": "2025-01-06",
        "summary": "Knowing how to properly report phishing attempts helps protect your entire organization from cyber threats.",
        "content": """
        <h2>Why reporting matters</h2>
        <p>Reporting suspicious emails helps:</p>
        <ul>
            <li>Protect other employees from the same threat</li>
            <li>Improve security awareness across the organization</li>
            <li>Allow IT to block malicious senders</li>
            <li>Track attack patterns and trends</li>
        </ul>
        
        <h2>What to report</h2>
        <p>Report emails that:</p>
        <ul>
            <li>Ask for passwords or sensitive information</li>
            <li>Contain suspicious links or attachments</li>
            <li>Create a sense of urgency or fear</li>
            <li>Come from unknown or suspicious senders</li>
            <li>Look like phishing attempts</li>
        </ul>
        
        <h2>How to report</h2>
        <p>Most organizations provide a "Report Phishing" button in email clients. You can also:</p>
        <ul>
            <li>Forward the email to your IT security team</li>
            <li>Use your company's security reporting portal</li>
            <li>Contact your IT help desk</li>
        </ul>
        
        <h2>What information to include</h2>
        <p>When reporting, include:</p>
        <ul>
            <li>The full email (as an attachment if possible)</li>
            <li>Sender's email address</li>
            <li>Date and time received</li>
            <li>Any actions you took (clicked link, opened attachment, etc.)</li>
        </ul>
        
        <h2>After reporting</h2>
        <ul>
            <li>Delete the suspicious email</li>
            <li>If you clicked a link, change your password immediately</li>
            <li>Run a virus scan if you opened an attachment</li>
            <li>Monitor your accounts for suspicious activity</li>
        </ul>
        """
    },
]

