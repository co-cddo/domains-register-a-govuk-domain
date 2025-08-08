import './base.cy'

describe('Errors when user skips and jumps pages', () => {

  it('Restarts a new session after completing an application', () => {
    let sessionCookie1;

    cy.deleteAllApplications()
    cy.visit('/')

    // First application
    cy.visit('/registrar-details/')
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.getCookie('sessionid').then(cookie => {
      sessionCookie1 = cookie.value;
    })

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(3) // Parish, small town or community council -> route 1
    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.enterDomainName('something-pc')
    cy.selectYesOrNo('domain_confirmation', 'yes')
    cy.get('p').should('include.text', 'For example, for parish councils the registrant must be the Clerk.')
    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')
    cy.fillOutRegistryDetails('Clerk', 'clerk@example.org')
    cy.summaryShouldHave(3, 'something-pc.gov.uk')
    cy.get('#id_submit').click()

    // Second application
    cy.visit('/registrar-details/')
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    // We should be starting a new session here
    cy.getCookie('sessionid').should(cookie => {
      expect(cookie).to.not.be.null;
      expect(cookie.value).to.not.equal(sessionCookie1)
    })
  })

  it('Throws a 400 when user skips to registry page', () => {
    cy.goToRegistrantType()
    cy.request({ url: '/registry-details', failOnStatusCode: false })
      .its('status').should('eq', 400)
  })

  it('Throws a 400 when user skips to success page', () => {
    cy.goToRegistrantDetails()
    cy.request({url: '/success', failOnStatusCode: false}).then(res => {
      expect(res.status).to.eq(400)
    })
  })

  it('Throws a 400 when user goes back 6 pages after submitting', () => {
    cy.goToConfirmation(1)
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')
    cy.go(-6)
    cy.checkPageTitleIncludes('Invalid request')
  })

  it('Throws a 400 when user goes back 4 pages after submitting', () => {
    cy.goToConfirmation(1)
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')
    cy.go(-4)
    cy.checkPageTitleIncludes('Invalid request')
  })

  it('Throws a 400 when user goes back and forth after submitting', () => {
    cy.goToConfirmation(1)
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')
    cy.go(-4)
    cy.checkPageTitleIncludes('Invalid request')
    cy.go(3)
    cy.checkPageTitleIncludes('Invalid request')
  })

  it('Throws a 400 when user goes back after submitting', () => {
    cy.goToConfirmation(1)
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')
    cy.go('back')
    cy.checkPageTitleIncludes('Invalid request')
  })

  it('Throws a 400 when user goes back 6 pages after submitting', () => {
    cy.goToConfirmation(1)
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')
    cy.go(-6)
    cy.checkPageTitleIncludes('Invalid request')
  })

  it('Throws a 400 when user goes back 4 pages after submitting', () => {
    cy.goToConfirmation(1)
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')
    cy.go(-4)
    cy.checkPageTitleIncludes('Invalid request')
  })

  it('Throws a 400 when user goes back and forth after submitting', () => {
    cy.goToConfirmation(1)
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')
    cy.go(-4)
    cy.checkPageTitleIncludes('Invalid request')
    cy.go(3)
    cy.checkPageTitleIncludes('Invalid request')
  })

  it('Throws a 400 when user goes back after submitting', () => {
    cy.goToConfirmation(1)
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')
    cy.go('back')
    cy.checkPageTitleIncludes('Invalid request')
  })
})
