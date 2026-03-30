"""
Bot Automation Script
Simulates bot behavior on the login form in real-time
Injects into browser to automate form filling
"""

class BotAutomation {
  constructor(botType = 'aggressive') {
    this.botType = botType;
    this.aadharInput = null;
    this.captchaInput = null;
    this.submitBtn = null;
    this.isRunning = false;

    console.log(`🤖 Bot Automation initialized: ${botType}`);
  }

  // Get form elements
  findFormElements() {
    this.aadharInput = document.querySelector('input[maxlength="12"]');
    this.captchaInput = document.querySelectorAll('input')[1];
    this.submitBtn = document.querySelector('button[type="submit"]');

    if (!this.aadharInput || !this.captchaInput || !this.submitBtn) {
      console.error('❌ Form elements not found!');
      return false;
    }

    console.log('✅ Form elements found');
    return true;
  }

  // Get delays based on bot type
  getDelays() {
    switch(this.botType) {
      case 'aggressive':
        return {
          beforeStart: 100,
          betweenChars: 5,      // Type very fast
          afterAadhar: 50,
          beforeCaptcha: 50,
          beforeSubmit: 100,
          totalTime: 1000       // Total time <1 second
        };

      case 'moderate':
        return {
          beforeStart: 500,
          betweenChars: 30,     // Fast but not inhuman
          afterAadhar: 200,
          beforeCaptcha: 200,
          beforeSubmit: 300,
          totalTime: 3000
        };

      case 'stealth':
        return {
          beforeStart: 1000,
          betweenChars: 80,     // Try to seem human
          afterAadhar: 500,
          beforeCaptcha: 500,
          beforeSubmit: 800,
          totalTime: 8000
        };

      case 'human':
        return {
          beforeStart: 2000,
          betweenChars: 100,    // Natural typing speed
          afterAadhar: 1000,
          beforeCaptcha: 1000,
          beforeSubmit: 2000,
          totalTime: 15000
        };
    }
  }

  // Type text character by character
  async typeText(element, text, delayBetweenChars) {
    for (let char of text) {
      element.value += char;

      // Trigger input event for React to detect change
      element.dispatchEvent(new Event('input', { bubbles: true }));
      element.dispatchEvent(new Event('change', { bubbles: true }));

      // Wait between characters
      await this.sleep(delayBetweenChars);
    }
  }

  // Sleep utility
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Run the bot automation
  async run() {
    if (this.isRunning) {
      console.log('⚠️ Bot already running!');
      return;
    }

    this.isRunning = true;
    const delays = this.getDelays();

    try {
      console.log(`\n${'='.repeat(60)}`);
      console.log(`🤖 STARTING BOT: ${this.botType.toUpperCase()}`);
      console.log(`${'='.repeat(60)}`);
      console.log(`Bot Type: ${this.botType}`);
      console.log(`Total Time: ~${delays.totalTime}ms`);
      console.log(`${'='.repeat(60)}\n`);

      // Find form elements
      if (!this.findFormElements()) {
        console.error('❌ Could not find form!');
        this.isRunning = false;
        return;
      }

      // Wait before starting
      console.log(`⏳ Waiting ${delays.beforeStart}ms before starting...`);
      await this.sleep(delays.beforeStart);

      // Type Aadhar number
      console.log('📝 Typing Aadhar number...');
      this.aadharInput.focus();
      await this.typeText(this.aadharInput, '987654321012', delays.betweenChars);
      console.log(`✅ Aadhar entered: ${this.aadharInput.value}`);

      // Wait
      await this.sleep(delays.afterAadhar);

      // Get captcha text from display
      const captchaDisplay = document.querySelector('.captcha-text');
      const captchaText = captchaDisplay ? captchaDisplay.textContent.trim() : 'XXXXXX';

      console.log(`📝 Typing CAPTCHA: ${captchaText}`);
      this.captchaInput.focus();
      await this.typeText(this.captchaInput, captchaText, delays.betweenChars);
      console.log(`✅ CAPTCHA entered: ${this.captchaInput.value}`);

      // Wait before submit
      console.log(`⏳ Waiting ${delays.beforeSubmit}ms before submitting...`);
      await this.sleep(delays.beforeSubmit);

      // Submit
      console.log(`🚀 Submitting form...`);
      this.submitBtn.click();

      console.log(`\n${'='.repeat(60)}`);
      console.log(`✅ Bot automation completed!`);
      console.log(`${'='.repeat(60)}\n`);

    } catch (error) {
      console.error('❌ Bot error:', error);
    } finally {
      this.isRunning = false;
    }
  }

  // Stop the bot
  stop() {
    this.isRunning = false;
    console.log('🛑 Bot stopped');
  }

  // Show status in console
  showStatus() {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🤖 Bot Status`);
    console.log(`${'='.repeat(60)}`);
    console.log(`Bot Type: ${this.botType}`);
    console.log(`Running: ${this.isRunning}`);
    console.log(`Aadhar: ${this.aadharInput?.value || 'Not found'}`);
    console.log(`CAPTCHA: ${this.captchaInput?.value || 'Not found'}`);
    console.log(`${'='.repeat(60)}\n`);
  }
}

// Global bot instance
window.bot = null;

// Helper functions for console
window.runBot = (type = 'aggressive') => {
  console.log(`🤖 Starting ${type} bot...`);
  window.bot = new BotAutomation(type);
  window.bot.run();
};

window.runAggressiveBot = () => window.runBot('aggressive');
window.runModerateBot = () => window.runBot('moderate');
window.runStealthBot = () => window.runBot('stealth');
window.runHumanBot = () => window.runBot('human');

window.stopBot = () => {
  if (window.bot) {
    window.bot.stop();
  }
};

window.botStatus = () => {
  if (window.bot) {
    window.bot.showStatus();
  } else {
    console.log('ℹ️ No bot running');
  }
};

console.log(`
=====================================
🤖 BOT AUTOMATION SCRIPT LOADED
=====================================

Available commands:

  🚀 runBot('aggressive')    - Fast bot (1 second)
  🚀 runBot('moderate')      - Medium speed bot (3 seconds)
  🚀 runBot('stealth')       - Slow bot (8 seconds)
  🚀 runBot('human')         - Human-like (15 seconds)

  Shortcuts:
  🚀 runAggressiveBot()
  🚀 runModerateBot()
  🚀 runStealthBot()
  🚀 runHumanBot()

  ⏹️  stopBot()               - Stop running bot
  📊 botStatus()             - Show bot status

=====================================
`);