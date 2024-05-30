import './base.cy'

describe('Changing answers at the end of the process', () => {

  it('lets you change registry details', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/registry-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.get('#id_registrant_role').should('have.value', 'Clerk')
    cy.get('#id_registrant_contact_email').should('have.value', 'clerk@example.org')

    // change a value
    cy.get('#id_registrant_role').clear().type('IT Support')

    // go back to answers
    cy.get('#id_submit').click()
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(10, 'IT Support')
  })


  it('lets you change registrant details', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/change-registrant-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrant details')
    cy.get('#id_registrant_organisation').should('have.value', 'HMRC')
    cy.get('#id_registrant_full_name').should('have.value', 'Rob Roberts')
    cy.get('#id_registrant_phone').should('have.value', '01225672344')
    cy.get('#id_registrant_email').should('have.value', 'rob@example.org')

    // change a value
    cy.get('#id_registrant_phone').clear().type('01225672345')

    // go back to answers
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(9, '01225672345')
  })


  it('lets you change registrar details', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/change-registrar-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrar details')
    cy.get('#id_registrar_name').should('have.value', 'Joe Bloggs')
    cy.get('#id_registrar_phone').should('have.value', '01225672345')
    cy.get('#id_registrar_email').should('have.value', 'joe@example.org')

    // change a value
    cy.get('#id_registrar_phone').clear().type('01225672345')

    // go back to answers
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(1, '01225672345')
  })


  it('lets you change your answer for the domain-purpose question', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/domain-purpose']").eq(0).click()
    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
    cy.get('input[type=radio]').eq(0).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // change the answer
    cy.chooseDomainPurpose(2) // Email only -> route 5

    // and see the new page
    cy.checkPageTitleIncludes('Does your registrant have proof of permission')
  })


  it('lets you change your answer about whether you have minister approval', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/minister']").eq(0).click()
    cy.checkPageTitleIncludes('Has a central government minister requested')
    cy.get('input[type=radio]').eq(0).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // change the answer
    cy.selectYesOrNo('minister', 'no')

    // and see the new page
    cy.checkPageTitleIncludes('Registrant details')
  })


  it('lets you change your answer about whether you have permission', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/written-permission']").eq(0).click()
    cy.checkPageTitleIncludes('Does your registrant have proof of permission')
    cy.get('input[type=radio]').eq(0).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // change the answer
    cy.selectYesOrNo('written_permission', 'no')

    // and fail
    cy.checkPageTitleIncludes('Your registrant does not have the evidence required to get a .gov.uk domain name')
  })


  it('lets you change your answer about whether you have an exemption', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/exemption']").eq(0).click()
    cy.checkPageTitleIncludes('Does your registrant have an exemption')
    cy.get('input[type=radio]').eq(0).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // change the answer
    cy.selectYesOrNo('exemption', 'no')

    // and fail
    cy.checkPageTitleIncludes('Your registrant cannot get approval for a .gov.uk domain name')
  })


  it('lets you change various details', () => {
    cy.goToConfirmation()
    cy.get("a[href='/change-registrar-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrar details')

    // check previously entered registrar details are pre-filled
    cy.get('#id_registrar_organisation').should('have.value', 'WeRegister')
    cy.get('#id_registrar_name').should('have.value', 'Joe Bloggs')
    cy.get('#id_registrar_phone').should('have.value', '01225672345')
    cy.get('#id_registrar_email').should('have.value', 'joe@example.org')

    // change a value
    cy.get('#id_registrar_phone').clear().type('01225672345')

    // go back to answers
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(1, '01225672345')

    // change a value to something wrong then correct it
    cy.get("a[href='/change-registrant-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrant details')
    cy.get('#id_registrant_phone').clear().type('2384')
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Registrant details')
    cy.confirmProblem('Enter a telephone number, like 01632 960 001 or 07700 900 982')
    cy.get('#id_registrant_phone').clear().type('01233456876')
    cy.get('#id_back_to_answers').click()
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(5, '01233456876')
  })


  it('doesn\'t let you come back to answers if you change the registrant type', () => {
    cy.goToConfirmation()
    cy.get("a[href='/registrant-type']").eq(0).click()
    cy.checkPageTitleIncludes('Who is this domain name for?')
    // check if value is pre-selected with the previous choice
    cy.get('input[type=radio]').eq(2).should('be.checked')

    // No going back to answers
    cy.get('#id_back_to_answers').should('not.exist')

    // Change route and check if we go to the expected new route
    cy.chooseRegistrantType(1) // Central government -> Route 2
    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
  })

  it('doesn\'t show the back-to-answers button when changing registry details', () => {
    cy.goToConfirmation(7)
    cy.get("a[href='/registry-details']").eq(0).click()
    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')

    // check previous answers are still there
    cy.get('#id_registrant_role').should('have.value', 'Clerk')
    cy.get('#id_registrant_contact_email').should('have.value', 'clerk@example.org')

    // No going back to answers because it's the last page before the confirmation page
    cy.get('#id_back_to_answers').should('not.exist')

    cy.fillOutRegistryDetails('Clerk', 'jim@example.com')
    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(10, ['Clerk', 'jim@example.com'])
  })

  it('doesn\'t ask for data again, even if you\'ve changed routes (route 5)', () => {
    cy.goToConfirmation(3)
    cy.get("a[href='/registrant-type']").click()
    cy.get('input[type=radio]').eq(3).should('be.checked')
    cy.chooseRegistrantType(1) // change to route 2
    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
    cy.get('input[type=radio]').should('not.be.checked')
    cy.chooseDomainPurpose(2) // Email address only -> Route 5

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.get('p').should('include.text', 'chief information officer')
    cy.selectYesOrNo('written_permission', 'yes')

    // permission was already uploaded so it should still show
    cy.checkPageTitleIncludes('Confirm uploaded evidence of permission to apply')
    cy.confirmUpload('permission.png')

    // same with domain name
    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.get('#id_domain_name').should('have.value', 'something-pc.gov.uk')
    cy.get('.govuk-button#id_submit').click();

    cy.checkPageTitleIncludes('Is something-pc.gov.uk the correct domain name?')
    cy.get('#id_domain_confirmation_1').should('be.checked')
    cy.get('.govuk-button#id_submit').click();

    cy.checkPageTitleIncludes('Has a central government minister requested the something-pc.gov.uk domain name?')
    // No radio button should be checked as we've not been here before
    cy.get('[type="radio"]').should('not.be.checked')
    cy.selectYesOrNo('minister', 'no')

    cy.checkPageTitleIncludes('Registrant details')
    cy.get('#id_registrant_organisation').should('have.value', 'HMRC')
    cy.get('#id_registrant_full_name').should('have.value', 'Rob Roberts')
    cy.get('#id_registrant_phone').should('have.value', '01225672344')
    cy.get('#id_registrant_email').should('have.value', 'rob@example.org')
    cy.get('#id_submit').click()

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.get('#id_registrant_role').should('have.value', 'Clerk')
    cy.get('#id_registrant_contact_email').should('have.value', 'clerk@example.org')
    cy.get('#id_submit').click()

    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(0, 'WeRegister')
    cy.summaryShouldHave(1, ['Joe Bloggs', '01225672345', 'joe@example.org'])
    cy.summaryShouldHave(2, 'Central government')
    cy.summaryShouldHave(3, 'Email only')
    cy.summaryShouldHave(4, ['Yes, evidence provided:', 'permission.png'])
    cy.summaryShouldHave(5, 'something-pc.gov.uk')
    cy.summaryShouldHave(6, 'No evidence provided')
    cy.summaryShouldHave(7, 'HMRC')
    cy.summaryShouldHave(8, ['Rob Roberts', '01225672344', 'rob@example.org'])
    cy.summaryShouldHave(9, ['Clerk', 'clerk@example.org'])
  })
})
