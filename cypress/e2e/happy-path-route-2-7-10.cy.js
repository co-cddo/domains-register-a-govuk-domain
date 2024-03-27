import './base.cy'

describe('Happy path - route 2-7-10', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'joe@example.org')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(1) // Central government -> Route 2

    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
    cy.chooseDomainPurpose(1) // Email+web -> Route 7

    cy.checkPageTitleIncludes('Does your registrant have an exemption from using the GOV.UK website?')
    cy.selectYesOrNo('exemption', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.uploadDocument("image.png")

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.confirmUpload('image.png')

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.get('p').should('include.text', 'chief executive')
    cy.selectYesOrNo('written_permission', 'no')

    cy.checkPageTitleIncludes('Your registrant does not have the evidence required to get a .gov.uk domain name')
    cy.get('p').should('include.text', 'chief executive')
  })
})
